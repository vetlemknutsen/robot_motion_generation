#include "my_qt_gui/main_window.hpp"

#include "ui_main_window.h"
#include <rclcpp/rclcpp.hpp>
#include <QMetaObject>
#include <QTimer>

MainWindow::MainWindow(std::shared_ptr<rclcpp::Node> node, QWidget *parent) : QMainWindow(parent), node_(node), ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    generate_client_ = node_->create_client<motion_pipeline_msgs::srv::GenerateRequest>("generate_rml");
    switch_robot_client_ = node_->create_client<motion_pipeline_msgs::srv::SwitchRobot>("switch_robot");

    send_pub_ = node_->create_publisher<std_msgs::msg::String>("send_webots", 10);
    log_sub_ = node_->create_subscription<motion_pipeline_msgs::msg::PipelineLog>("pipeline_logs", 10, std::bind(&MainWindow::onLogReceived, this, std::placeholders::_1));

    connect(
        ui->generateButton,
        &QPushButton::clicked,
        this,
        &MainWindow::onGenerateClicked);

    connect(
        ui->browseButton,
        &QPushButton::clicked,
        this,
        &MainWindow::onBrowseClicked);

    connect(
        ui->sendButton,
        &QPushButton::clicked,
        this,
        &MainWindow::onSendClicked);

    connect(
        ui->robotBox,
        &QComboBox::currentTextChanged, 
        this, 
        &MainWindow::onRobotDropdownChanged);


    ui->txt_logs->appendPlainText("Ready!");

    current_robot_ = "nao";
}

void MainWindow::onGenerateClicked(){
    if(robot_loading_){
        return;
    }

    QString path = ui->pathLineEdit->text();
    QString adapter = ui->adapterBox->currentText();
    QString robot = ui->robotBox->currentText();

    ui->lbl_metadata->setText("File: " + path + "   |   " + "Adapter: " + adapter +  "   |   " + "Robot: " + robot);
    ui->txt_logs->appendPlainText("Generate request sent");

    auto request = std::make_shared<motion_pipeline_msgs::srv::GenerateRequest::Request>();
    request->input_path = path.toStdString();
    request->adapter = adapter.toStdString();
    request->robot = robot.toStdString();

    generate_client_->async_send_request(request, 
    [this](rclcpp::Client<motion_pipeline_msgs::srv::GenerateRequest>::SharedFuture future){
        auto response = future.get();
        QMetaObject::invokeMethod(this, [this, response](){
            if (response->success)
                ui->txt_editor->setPlainText(QString::fromStdString(response->rml_text));
        });
    });
    
}

void MainWindow::onBrowseClicked(){
    QFileDialog dialog(this);
    dialog.setFileMode(QFileDialog::ExistingFile);

    QStringList fileNames;
    if (dialog.exec())
        fileNames = dialog.selectedFiles();
    if (!fileNames.isEmpty()){
        QString fileName = fileNames.at(0);
        ui->pathLineEdit->setText(fileName);
    }
}

void MainWindow::onSendClicked(){
    QString rmlPlain = ui->txt_editor->toPlainText();
    std_msgs::msg::String msg;
    msg.data = rmlPlain.toStdString();
    send_pub_->publish(msg);

}

void MainWindow::onRobotDropdownChanged(const QString& robot){
    if (robot == current_robot_ || robot.isEmpty()){
        return;
    }

    setLoadingState(true);

    auto request = std::make_shared<motion_pipeline_msgs::srv::SwitchRobot::Request>();
    request->name = robot.toStdString();

    switch_robot_client_->async_send_request(request,
        [this,robot](rclcpp::Client<motion_pipeline_msgs::srv::SwitchRobot>::SharedFuture future){
            future.get();
            QMetaObject::invokeMethod(this, [this, robot](){
                current_robot_ = robot; 
                QTimer::singleShot(3000, this, [this](){setLoadingState(false); });
        });
    });
};


void MainWindow::setLoadingState(bool loading){
    robot_loading_ = loading;
    ui->generateButton->setEnabled(!loading);
    ui->robotBox->setEnabled(!loading);
    
    if (loading) {
        ui->generateButton->setText("Loading...");
    } else {
        ui->generateButton->setText("Generate");
    }
}

void MainWindow::onLogReceived(const motion_pipeline_msgs::msg::PipelineLog::SharedPtr msg){
    QString text = QString::fromStdString(msg->message);
    QMetaObject::invokeMethod(this, [this, text](){
        ui->txt_logs->appendPlainText(text);
    });
}


MainWindow::~MainWindow(){
    delete ui;
}
