#include "my_qt_gui/main_window.hpp"
#include "ui_main_window.h"
#include "my_qt_gui/editor_panel.hpp"
#include "my_qt_gui/options_panel.hpp"

MainWindow::MainWindow(std::shared_ptr<rclcpp::Node> node, QWidget* parent)
: QMainWindow(parent), node_(node), ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    ui->splitter->setSizes({200, 500, 300});

    editorPanel_ = new EditorPanel(
        node_,
        ui->txt_editor,
        ui->txt_logs,
        ui->lbl_metadata,
        ui->sendButton,
        this);

    optionsPanel_ = new OptionsPanel(
        node_,
        ui->pathLineEdit,
        ui->adapterBox,
        ui->robotBox,
        ui->generateButton,
        ui->browseButton,
        ui->label,
        this);

    connect(optionsPanel_, &OptionsPanel::generateStarted, this, [this](const QString& metadata) {
        editorPanel_->setMetadata(metadata);
        editorPanel_->showSpinner(true);
    });

    connect(optionsPanel_, &OptionsPanel::rmlGenerated, editorPanel_, &EditorPanel::setRml);

    connect(optionsPanel_, &OptionsPanel::generateFailed, this, [this](const QString&) {
        editorPanel_->showSpinner(false);
    });

    connect(optionsPanel_, &OptionsPanel::logMessage, editorPanel_, &EditorPanel::appendLog);

    editorPanel_->appendLog("Ready!");
}

MainWindow::~MainWindow()
{
    delete ui;
}
