#include "my_qt_gui/main_window.hpp"

#include "ui_main_window.h"
#include <rclcpp/rclcpp.hpp>
#include <QMetaObject>

MainWindow::MainWindow(std::shared_ptr<rclcpp::Node> node, QWidget *parent) : QMainWindow(parent), node_(node), ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    generate_pub_ = node_->create_publisher<std_msgs::msg::String>("generate_request", 10);
    rml_sub_ = node_->create_subscription<std_msgs::msg::String>("rml_output", 10, std::bind(&MainWindow::onRmlReceived, this, std::placeholders::_1));

    send_pub_ = node_->create_publisher<std_msgs::msg::String>("send_webots", 10);

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


    statusBar()->showMessage("Ready!");
}

void MainWindow::onGenerateClicked(){
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



MainWindow::~MainWindow(){
    delete ui;
}

