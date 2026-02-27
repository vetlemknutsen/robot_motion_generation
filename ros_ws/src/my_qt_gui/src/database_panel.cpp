#include "my_qt_gui/database_panel.hpp"
#include <QMetaObject>
#include <QTimer>

DatabasePanel::DatabasePanel(std::shared_ptr<rclcpp::Node> node,
                             QListWidget* list,
                             QPushButton* loadButton,
                             QPushButton* deleteButton,
                             QWidget* parent)
: QWidget(parent), node_(node), list_(list)
{
    get_motions_client_  = node_->create_client<motion_pipeline_msgs::srv::GetMotions>("get_motions");
    save_motion_client_  = node_->create_client<motion_pipeline_msgs::srv::SaveMotion>("save_motion");
    delete_motion_client_ = node_->create_client<motion_pipeline_msgs::srv::DeleteMotion>("delete_motion");

    connect(loadButton,   &QPushButton::clicked, this, &DatabasePanel::onLoadClicked);
    connect(deleteButton, &QPushButton::clicked, this, &DatabasePanel::onDeleteClicked);

    refresh();
}

void DatabasePanel::refresh()
{
    if (!get_motions_client_->service_is_ready()){
        QTimer::singleShot(200, this, &DatabasePanel::refresh);
        return;
    }
    auto request = std::make_shared<motion_pipeline_msgs::srv::GetMotions::Request>();
    get_motions_client_->async_send_request(request,
        [this](rclcpp::Client<motion_pipeline_msgs::srv::GetMotions>::SharedFuture future) {
            auto response = future.get();
            QMetaObject::invokeMethod(this, [this, response]() {
                list_->clear();
                for (size_t i = 0; i < response->names.size(); i++) {
                    auto* item = new QListWidgetItem(
                        QString::fromStdString(response->names[i]) +
                        " (" + QString::fromStdString(response->robots[i]) + ")"
                    );
                    item->setData(Qt::UserRole, response->ids[i]);
                    item->setData(Qt::UserRole + 1, QString::fromStdString(response->rmls[i]));
                    list_->addItem(item);
                }
            });
        });
}

void DatabasePanel::saveMotion(const QString& name, const QString& robot, const QString& rml)
{
    auto request = std::make_shared<motion_pipeline_msgs::srv::SaveMotion::Request>();
    request->name  = name.toStdString();
    request->robot = robot.toStdString();
    request->rml   = rml.toStdString();

    save_motion_client_->async_send_request(request,
        [this](rclcpp::Client<motion_pipeline_msgs::srv::SaveMotion>::SharedFuture future) {
            future.get();
            QMetaObject::invokeMethod(this, [this]() { 
                refresh(); 
            });
        });
}

void DatabasePanel::onLoadClicked()
{
    auto* item = list_->currentItem();
    if (!item) return;
    emit motionLoaded(item->data(Qt::UserRole + 1).toString());
}

void DatabasePanel::onDeleteClicked()
{
    auto* item = list_->currentItem();
    if (!item) return;

    auto request = std::make_shared<motion_pipeline_msgs::srv::DeleteMotion::Request>();
    request->id = item->data(Qt::UserRole).toInt();

    delete_motion_client_->async_send_request(request,
        [this](rclcpp::Client<motion_pipeline_msgs::srv::DeleteMotion>::SharedFuture future) {
            future.get();
            QMetaObject::invokeMethod(this, [this]() { 
                refresh(); 
            });
        });
}
