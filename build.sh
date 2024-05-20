#!/bin/bash

# 定义变量
PROJECT_NAME="super_shell"
ENTRY_POINT="main.py"
DIST_DIR="dist"
BUILD_DIR="build"
SPEC_FILE="${PROJECT_NAME}.spec"

# 清理之前的构建
echo "Cleaning up previous builds..."
rm -rf ${DIST_DIR} ${BUILD_DIR} ${SPEC_FILE}

# 使用 PyInstaller 打包项目
echo "Packaging project into a single executable..."
pyinstaller --onefile --name ${PROJECT_NAME} ${ENTRY_POINT}

# 确认打包成功
if [ -f "${DIST_DIR}/${PROJECT_NAME}" ]; then
    echo "Packaging successful. Executable created at ${DIST_DIR}/${PROJECT_NAME}"
else
    echo "Packaging failed."
    exit 1
fi

# 设置执行权限
echo "Setting execute permissions..."
chmod +x ${DIST_DIR}/${PROJECT_NAME}

echo "Build script completed."