#pragma once
#include <QWidget>
#include <QPlainTextEdit>
#include <QLabel>
#include <QPushButton>
#include <QMovie>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>
#include <motion_pipeline_msgs/msg/log_message.hpp>

class EditorPanel : public QWidget
{
    Q_OBJECT

public:
    EditorPanel(std::shared_ptr<rclcpp::Node> node, QPlainTextEdit* editor, QPlainTextEdit* logs, QLabel* metadata, QPushButton* sendButton, QPushButton* saveButton, QWidget* parent = nullptr);

    QString getRml() const;

public slots:
    void setRml(const QString& rml);
    void setMetadata(const QString& text);
    void showSpinner(bool visible);
    void appendLog(const QString& text);

signals:
    void saveRequested(const QString& rml);

private slots:
    void onSendClicked();
    void onLogReceived(const motion_pipeline_msgs::msg::LogMessage::SharedPtr msg);

private:
    bool eventFilter(QObject* obj, QEvent* event) override;

    std::shared_ptr<rclcpp::Node> node_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr send_pub_;
    rclcpp::Subscription<motion_pipeline_msgs::msg::LogMessage>::SharedPtr log_sub_;

    QPlainTextEdit* editor_;
    QPlainTextEdit* logs_;
    QLabel* metadata_;
    QLabel* spinnerLabel_;
    QMovie* spinner_;
};
