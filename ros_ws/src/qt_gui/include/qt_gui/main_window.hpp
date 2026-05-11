#pragma once
#include <QMainWindow>
#include <memory>
#include <rclcpp/rclcpp.hpp>

namespace Ui { class MainWindow; }
class EditorPanel;
class OptionsPanel;
class DatabasePanel;

class MainWindow : public QMainWindow
{
public:
    MainWindow(std::shared_ptr<rclcpp::Node> node, QWidget* parent = nullptr);
    ~MainWindow();

private:
    std::shared_ptr<rclcpp::Node> node_;
     Ui::MainWindow* ui;

    EditorPanel* editorPanel_;
    OptionsPanel* optionsPanel_;
    DatabasePanel* databasePanel_;
};
