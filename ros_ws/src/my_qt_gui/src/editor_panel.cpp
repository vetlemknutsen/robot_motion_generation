#include "my_qt_gui/editor_panel.hpp"
#include <QEvent>
#include <QMetaObject>

EditorPanel::EditorPanel(std::shared_ptr<rclcpp::Node> node, QPlainTextEdit* editor, QPlainTextEdit* logs, QLabel* metadata, QPushButton* sendButton, QPushButton* saveButton, QWidget* parent)
: QWidget(parent), node_(node), editor_(editor), logs_(logs), metadata_(metadata)
{
    send_pub_ = node_->create_publisher<std_msgs::msg::String>("rml_for_execution", 10);
    log_sub_ = node_->create_subscription<motion_pipeline_msgs::msg::LogMessage>("pipeline_logs", 10, std::bind(&EditorPanel::onLogReceived, this, std::placeholders::_1));

    spinner_ = new QMovie("src/my_qt_gui/resources/loading.gif");
    spinnerLabel_ = new QLabel(editor_);
    spinnerLabel_->setMovie(spinner_);
    spinnerLabel_->setFixedSize(64, 64);
    spinnerLabel_->setScaledContents(true);
    spinnerLabel_->hide();

    editor_->installEventFilter(this);

    connect(sendButton, &QPushButton::clicked, this, &EditorPanel::onSendClicked);

    connect(saveButton, &QPushButton::clicked, this, [this](){
        emit saveRequested(editor_->toPlainText());
    });
}

QString EditorPanel::getRml() const { 
    return editor_->toPlainText(); 
}

void EditorPanel::setRml(const QString& rml){
    spinner_->stop();
    spinnerLabel_->hide();
    editor_->setPlainText(rml);
}

void EditorPanel::setMetadata(const QString& text) { 
    metadata_->setText(text); 
}

void EditorPanel::showSpinner(bool visible){
    if (visible) {
        editor_->clear();
        spinnerLabel_->move((editor_->width() - 64) / 2, (editor_->height() - 64) / 2);
        spinnerLabel_->show();
        spinner_->start();
    } else {
        spinner_->stop();
        spinnerLabel_->hide();
    }
}

void EditorPanel::onSendClicked(){
    std_msgs::msg::String msg;
    msg.data = editor_->toPlainText().toStdString();
    send_pub_->publish(msg);
}

void EditorPanel::onLogReceived(const motion_pipeline_msgs::msg::LogMessage::SharedPtr msg){
    QString text = QString::fromStdString(msg->message);
    QMetaObject::invokeMethod(this, [this, msg, text]() {
        QString color = (msg->level == motion_pipeline_msgs::msg::LogMessage::ERROR) ? "#ff0000" : "#008000";
        logs_ -> appendHtml(QString("<span style='color:%1'>%2</span>").arg(color).arg(text.toHtmlEscaped()));
    });
}

bool EditorPanel::eventFilter(QObject* obj, QEvent* event){
    if (obj == editor_ && event->type() == QEvent::Resize) {
        spinnerLabel_->move((editor_->width() - 64) / 2, (editor_->height() - 64) / 2);
    }
    return QWidget::eventFilter(obj, event);
}


void EditorPanel::appendLog(const QString& text) { 
    logs_->appendHtml(QString("<span style='color:#008000'>%1</span>")
    .arg(text.toHtmlEscaped()));

}

