#include "generation_gui/database_panel.hpp"
#include <QMetaObject>
#include <QTimer>

/**
 * Database panel: lists saved motions and provides load/save/delete.
 * Talks to the bridge's /get_motions, /save_motion, /delete_motion
 * services. Calls refresh() after every write so the list stays in sync.
 */
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

    // populate the list on startup
    refresh();
}

/// Reload the motion list from the backend. 
/// Retry every 200 ms, since service may not be up at startup 
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

/// Save a motion, then refresh
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

/// Emit the selectd motion's RML
void DatabasePanel::onLoadClicked()
{
    auto* item = list_->currentItem();
    if (!item) return;
    emit motionLoaded(item->data(Qt::UserRole + 1).toString());
}

/// Delete selected motion and refresh
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
