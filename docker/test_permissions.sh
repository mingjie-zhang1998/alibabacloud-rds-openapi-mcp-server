#!/bin/bash
# 权限测试脚本
# 用于验证日志文件权限是否正确设置

echo "=== 权限测试脚本 ==="

# 检查当前用户
echo "当前用户: $(whoami)"
echo "用户ID: $(id)"

# 检查目录权限
echo -e "\n=== 目录权限检查 ==="
for dir in /app /app/logs /tmp/logs; do
    if [ -d "$dir" ]; then
        ls -ld "$dir"
        if [ -w "$dir" ]; then
            echo "✅ $dir 可写"
        else
            echo "❌ $dir 不可写"
        fi
    else
        echo "❌ 目录 $dir 不存在"
    fi
done

# 检查是否存在目录冲突
echo -e "\n=== 目录/文件冲突检查 ==="
for path in /app/app.log; do
    if [ -d "$path" ]; then
        echo "❌ $path 是目录（应该是文件）"
    elif [ -f "$path" ]; then
        echo "✅ $path 是文件"
    else
        echo "⚠️ $path 不存在"
    fi
done

# 测试文件创建
echo -e "\n=== 文件创建测试 ==="
test_files=(
    "/app/test_app.log"
    "/app/logs/test_access.log"
    "/app/logs/test_error.log"
)

for test_file in "${test_files[@]}"; do
    echo "测试创建: $test_file"
    
    # 尝试创建文件
    if > "$test_file" 2>/dev/null; then
        echo "✅ 创建成功"
        
        # 尝试写入
        if echo "Test log entry" > "$test_file" 2>/dev/null; then
            echo "✅ 写入成功"
        else
            echo "❌ 写入失败"
        fi
        
        # 显示文件权限
        ls -l "$test_file"
        
        # 清理测试文件
        rm -f "$test_file"
    else
        echo "❌ 创建失败"
    fi
    echo
done

# 检查实际日志文件
echo "=== 实际日志文件检查 ==="
log_files=(
    "/app/app.log"
    "/app/logs/access.log"
    "/app/logs/error.log"
)

for log_file in "${log_files[@]}"; do
    echo "检查: $log_file"
    if [ -f "$log_file" ]; then
        ls -l "$log_file"
        if [ -w "$log_file" ]; then
            echo "✅ 文件可写"
        else
            echo "❌ 文件不可写"
        fi
    elif [ -d "$log_file" ]; then
        echo "❌ 是目录（应该是文件）"
    else
        echo "❌ 文件不存在"
    fi
    echo
done

echo "=== 权限测试完成 ===" 