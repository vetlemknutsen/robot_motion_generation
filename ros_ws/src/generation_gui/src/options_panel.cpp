#include "generation_gui/options_panel.hpp"
#include <QMetaObject>
#include <QTimer>
#include <QFileInfo>

/**
 * Options panel. input file, adapter, robot dropdown, and Generate button.
 * Calls /generate_rml and /switch_robot. 
 */
OptionsPanel::OptionsPanel(std::shared_ptr<rclcpp::Node> node, QLineEdit* pathEdit, QComboBox* adapterBox, QComboBox* robotBox, QPushButton* generateButton, QPushButton* browseButton, QWidget* parent)
: QWidget(parent), node_(node),
  pathEdit_(pathEdit), adapterBox_(adapterBox), robotBox_(robotBox),
  generateButton_(generateButton)
{
    generate_client_ = node_->create_client<motion_pipeline_msgs::srv::GenerateRequest>("generate_rml");
    switch_robot_client_ = node_->create_client<motion_pipeline_msgs::srv::SwitchRobot>("switch_robot");

    connect(generateButton_, &QPushButton::clicked, this, &OptionsPanel::onGenerateClicked);
    connect(browseButton, &QPushButton::clicked, this, &OptionsPanel::onBrowseClicked);
    connect(robotBox_, &QComboBox::currentTextChanged, this, &OptionsPanel::onRobotChanged);
}

/// Build a GenerateRequest from the current UI state and send it. 
void OptionsPanel::onGenerateClicked()
{
    if (robotLoading_) return;

    QString path = pathEdit_->text();
    QString adapter = adapterBox_->currentText();
    QString robot = robotBox_->currentText();
    QString metadata = "File: " + QFileInfo(path).fileName() + "   |   Adapter: " + adapter + "   |   Robot: " + robot;

    emit generateStarted(metadata);
    emit logMessage("Generate request sent...");

    auto request = std::make_shared<motion_pipeline_msgs::srv::GenerateRequest::Request>();
    request->input_path = path.toStdString();
    request->adapter = adapter.toLower().toStdString();
    request->robot = robot.toLower().toStdString();

    // async so we don't block the UI thread waiting for IK
    generate_client_->async_send_request(request,
        [this](rclcpp::Client<motion_pipeline_msgs::srv::GenerateRequest>::SharedFuture future) {
            auto response = future.get();
            QMetaObject::invokeMethod(this, [this, response]() {
                if (response->success) {
                    emit rmlGenerated(QString::fromStdString(response->rml_text));
                    emit logMessage("RML generated successfully.");
                } else {
                    emit generateFailed(QString::fromStdString(response->error_message));
                    
                }
            });
        });
}

/// Open a native file picker and put the chosen path into the line edit
void OptionsPanel::onBrowseClicked()
{
    QFileDialog dialog(this);
    dialog.setFileMode(QFileDialog::ExistingFile);
    QStringList files;
    if (dialog.exec())
        files = dialog.selectedFiles();
    if (!files.isEmpty())
        pathEdit_->setText(files.at(0));
}

/// Robot dropdown changed. Ask backend to load the robot's MoveIt.
void OptionsPanel::onRobotChanged(const QString& robot)
{
    if (robot.toLower() == currentRobot_.toLower() || robot.isEmpty()) return;

    setLoadingState(true);

    auto request = std::make_shared<motion_pipeline_msgs::srv::SwitchRobot::Request>();
    request->name = robot.toLower().toStdString();

    switch_robot_client_->async_send_request(request,
        [this, robot](rclcpp::Client<motion_pipeline_msgs::srv::SwitchRobot>::SharedFuture future) {
            future.get();
            QMetaObject::invokeMethod(this, [this, robot]() {
                currentRobot_ = robot;
                QTimer::singleShot(3000, this, [this]() { setLoadingState(false); });
            });
        });
}

/// Grey out or re-enable controls during a robot switch
void OptionsPanel::setLoadingState(bool loading)
{
    robotLoading_ = loading;
    generateButton_->setEnabled(!loading);
    robotBox_->setEnabled(!loading);
    generateButton_->setText(loading ? "Loading..." : "Generate");
}
