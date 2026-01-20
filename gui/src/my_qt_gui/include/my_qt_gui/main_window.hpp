#pragma once

#include <QMainWindow>
#include <memory>

namespace rclcpp {
    class Node;
}

namespace Ui {
    class MainWindow;
}

class MainWindow : public QMainWindow
{

public:
    MainWindow(std::shared_ptr<rclcpp::Node> node, QWidget *parent=nullptr);
    ~MainWindow();
private:
    std::shared_ptr<rclcpp::Node> node_;
    Ui::MainWindow *ui;
};