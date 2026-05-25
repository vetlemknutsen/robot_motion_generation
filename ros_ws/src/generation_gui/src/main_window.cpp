#include "generation_gui/main_window.hpp"
#include "ui_main_window.h"
#include "generation_gui/editor_panel.hpp"
#include "generation_gui/options_panel.hpp"
#include "generation_gui/database_panel.hpp"
#include <QInputDialog>

/**
 * Top-level window. Owns the three side panels (editor, options, database)
 * and wires their Qt signals together so they can communicate without
 * holding references to each other directly.
 *
 * @param node Shared ROS node, passed down to every panel so they share
 *             one set of publishers/subscribers/clients.
 * @param parent Standard Qt parent pointer.
 */
MainWindow::MainWindow(std::shared_ptr<rclcpp::Node> node, QWidget* parent)
: QMainWindow(parent), node_(node), ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    // splitter sizes: left (options) | middle (editor) | right (database)
    ui->splitter->setSizes({200, 500, 300});

    // each panel gets the widgets it controls
    editorPanel_ = new EditorPanel(
        node_,
        ui->txt_editor,
        ui->txt_logs,
        ui->lbl_metadata,
        ui->sendButton,
        ui->saveMotionButton,
        this);

    optionsPanel_ = new OptionsPanel(
        node_,
        ui->pathLineEdit,
        ui->adapterBox,
        ui->robotBox,
        ui->generateButton,
        ui->browseButton,
        this);

    databasePanel_ = new DatabasePanel(
        node_, 
        ui->listWidget,
        ui->loadMotionButton, 
        ui->deleteMotionButton, 
        this
    );

    // when generation starts, show the spinner and update metadata 
    connect(optionsPanel_, &OptionsPanel::generateStarted, this, [this](const QString& metadata) {
        editorPanel_->setMetadata(metadata);
        editorPanel_->showSpinner(true);
    });

    // result arrives, dorp the text into the editor
    connect(optionsPanel_, &OptionsPanel::rmlGenerated, editorPanel_, &EditorPanel::setRml);

    // failure, just hide the spinner, the erorr is displayed in log
    connect(optionsPanel_, &OptionsPanel::generateFailed, this, [this](const QString&) {
        editorPanel_->showSpinner(false);
    });

    connect(optionsPanel_, &OptionsPanel::logMessage, editorPanel_, &EditorPanel::appendLog);

    // load motion text into editor
    connect(databasePanel_, &DatabasePanel::motionLoaded, editorPanel_, &EditorPanel::setRml);

    // editors save button, name dialog, save
    connect(editorPanel_, &EditorPanel::saveRequested, this, [this](const QString& rml){
        bool ok;
        QString name = QInputDialog::getText(this, "Save Motion", "Name:", QLineEdit::Normal, "", &ok);
        databasePanel_->saveMotion(name, optionsPanel_->getCurrentRobot(), rml);
    });

    editorPanel_->appendLog("Ready!");
}

MainWindow::~MainWindow()
{
    delete ui;
}
