#pragma once
#include <QWidget>
#include <QListWidget>
#include <QPushButton>
#include <rclcpp/rclcpp.hpp>
#include <motion_pipeline_msgs/srv/get_motions.hpp>
#include <motion_pipeline_msgs/srv/save_motion.hpp>
#include <motion_pipeline_msgs/srv/delete_motion.hpp>

class DatabasePanel : public QWidget
{
    Q_OBJECT

public:
    DatabasePanel(std::shared_ptr<rclcpp::Node> node,
                  QListWidget* list,
                  QPushButton* loadButton,
                  QPushButton* deleteButton,
                  QWidget* parent = nullptr);

    void saveMotion(const QString& name, const QString& robot, const QString& rml);
    void refresh();

signals:
    void motionLoaded(const QString& rml);

private slots:
    void onLoadClicked();
    void onDeleteClicked();

private:
    std::shared_ptr<rclcpp::Node> node_;
    rclcpp::Client<motion_pipeline_msgs::srv::GetMotions>::SharedPtr get_motions_client_;
    rclcpp::Client<motion_pipeline_msgs::srv::SaveMotion>::SharedPtr save_motion_client_;
    rclcpp::Client<motion_pipeline_msgs::srv::DeleteMotion>::SharedPtr delete_motion_client_;

    QListWidget* list_;
};
