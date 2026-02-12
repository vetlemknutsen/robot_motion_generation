#include "my_qt_gui/main_window.hpp"

#include "ui_main_window.h"
#include <rclcpp/rclcpp.hpp>
#include <QMetaObject>
#include <QTimer>

MainWindow::MainWindow(std::shared_ptr<rclcpp::Node> node, QWidget *parent) : QMainWindow(parent), node_(node), ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    generate_pub_ = node_->create_publisher<std_msgs::msg::String>("generate_request", 10);
    rml_sub_ = node_->create_subscription<std_msgs::msg::String>("rml_output", 10, std::bind(&MainWindow::onRmlReceived, this, std::placeholders::_1));

    send_pub_ = node_->create_publisher<std_msgs::msg::String>("send_webots", 10);

    switch_robot_pub_ = node_->create_publisher<std_msgs::msg::String>("switch_robot", 10);
    robot_ready_sub_ = node_->create_subscription<std_msgs::msg::String>("robot_ready", 10, std::bind(&MainWindow::onRobotReady, this, std::placeholders::_1));

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


    statusBar()->showMessage("Ready!");

    current_robot_ = "nao";
}

void MainWindow::onGenerateClicked(){
    if(robot_loading_){
        return;
    }

    QString path = ui->pathLineEdit->text();
    QString adapter = ui->adapterBox->currentText();
    QString robot = ui->robotBox->currentText();

    std_msgs::msg::String msg;
    msg.data = "{\"input_path\":\"" + path.toStdString() +
               "\", \"adapter\":\"" + adapter.toStdString() +
               "\",\"robot\":\"" + robot.toStdString() + "\"}";

    generate_pub_->publish(msg);
    ui->lbl_metadata->setText("File: " + path + "   |   " + "Adapter: " + "   |   " + "Robot: " + robot);
    statusBar()->showMessage("Generate request sent");
}

void MainWindow::onRmlReceived(const std_msgs::msg::String::SharedPtr msg){
    QString rml = QString::fromStdString(msg->data);
    QMetaObject::invokeMethod(this, [this, rml]() {
        ui->txt_editor->setPlainText(rml);
        statusBar()->showMessage("RML received");
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
    statusBar()->showMessage("Loading " + robot + "...");

    std_msgs::msg::String msg; 
    msg.data = robot.toStdString();
    switch_robot_pub_->publish(msg);
}

void MainWindow::onRobotReady(const std_msgs::msg::String::SharedPtr msg){
    QString robot = QString::fromStdString(msg->data);
    QMetaObject::invokeMethod(this, [this, robot]() {
        current_robot_ = robot;

        QTimer::singleShot(3000, this, [this, robot](){
            setLoadingState(false);
            statusBar()->showMessage(robot + " ready!");
        });
    
    });
}

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



MainWindow::~MainWindow(){
    delete ui;
}
