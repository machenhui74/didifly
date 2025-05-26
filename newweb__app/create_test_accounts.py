#!/usr/bin/env python3
"""
创建测试账号脚本
为每个权限级别创建3个测试账号
"""

import sys
import os
from werkzeug.security import generate_password_hash

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_accounts():
    """创建测试账号"""
    print("🚀 开始创建测试账号...")
    
    try:
        # 创建Flask应用上下文
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from logic.auth import UserRole, USERS, save_users
            
            # 定义测试账号数据
            test_accounts = [
                # 管理员账号 (3个)
                {
                    'username': 'admin1',
                    'password': 'admin123',
                    'name': '系统管理员1',
                    'store': '总部',
                    'role': UserRole.ADMIN
                },
                {
                    'username': 'admin2', 
                    'password': 'admin123',
                    'name': '系统管理员2',
                    'store': '总部',
                    'role': UserRole.ADMIN
                },
                {
                    'username': 'admin3',
                    'password': 'admin123', 
                    'name': '系统管理员3',
                    'store': '总部',
                    'role': UserRole.ADMIN
                },
                
                # 校长账号 (3个)
                {
                    'username': 'principal1',
                    'password': 'principal123',
                    'name': '校长张三',
                    'store': '北京训练中心',
                    'role': UserRole.PRINCIPAL
                },
                {
                    'username': 'principal2',
                    'password': 'principal123',
                    'name': '校长李四',
                    'store': '上海训练中心', 
                    'role': UserRole.PRINCIPAL
                },
                {
                    'username': 'principal3',
                    'password': 'principal123',
                    'name': '校长王五',
                    'store': '广州训练中心',
                    'role': UserRole.PRINCIPAL
                },
                
                # 测评师账号 (3个)
                {
                    'username': 'assessor1',
                    'password': 'assessor123',
                    'name': '测评师赵六',
                    'store': '北京训练中心',
                    'role': UserRole.ASSESSOR
                },
                {
                    'username': 'assessor2',
                    'password': 'assessor123',
                    'name': '测评师孙七',
                    'store': '上海训练中心',
                    'role': UserRole.ASSESSOR
                },
                {
                    'username': 'assessor3',
                    'password': 'assessor123',
                    'name': '测评师周八',
                    'store': '广州训练中心',
                    'role': UserRole.ASSESSOR
                },
                
                # 老师账号 (3个)
                {
                    'username': 'teacher1',
                    'password': 'teacher123',
                    'name': '老师吴九',
                    'store': '北京训练中心',
                    'role': UserRole.TEACHER
                },
                {
                    'username': 'teacher2',
                    'password': 'teacher123',
                    'name': '老师郑十',
                    'store': '上海训练中心',
                    'role': UserRole.TEACHER
                },
                {
                    'username': 'teacher3',
                    'password': 'teacher123',
                    'name': '老师钱一',
                    'store': '广州训练中心',
                    'role': UserRole.TEACHER
                }
            ]
            
            created_count = 0
            skipped_count = 0
            
            for account in test_accounts:
                username = account['username']
                
                # 检查用户是否已存在
                if username in USERS:
                    print(f"⚠️  用户 {username} 已存在，跳过创建")
                    skipped_count += 1
                    continue
                
                # 创建用户数据
                user_data = {
                    'password': generate_password_hash(account['password']),
                    'name': account['name'],
                    'store': account['store'],
                    'role': account['role'],
                    'is_encrypted': True
                }
                
                # 为校长添加额外字段
                if account['role'] == UserRole.PRINCIPAL:
                    user_data.update({
                        'created_users_count': 0,
                        'created_users_list': []
                    })
                
                # 添加到用户数据
                USERS[username] = user_data
                created_count += 1
                
                print(f"✅ 创建用户: {username} ({account['name']}) - {account['role']}")
            
            # 保存用户数据
            if created_count > 0:
                if save_users(USERS):
                    print(f"\n🎉 成功创建 {created_count} 个测试账号！")
                    if skipped_count > 0:
                        print(f"📝 跳过 {skipped_count} 个已存在的账号")
                else:
                    print("❌ 保存用户数据失败！")
                    return False
            else:
                print("📝 没有新账号需要创建")
            
            # 显示账号信息
            print("\n📋 测试账号信息:")
            print("=" * 60)
            
            role_names = {
                UserRole.ADMIN: "管理员",
                UserRole.PRINCIPAL: "校长", 
                UserRole.ASSESSOR: "测评师",
                UserRole.TEACHER: "老师"
            }
            
            for role in [UserRole.ADMIN, UserRole.PRINCIPAL, UserRole.ASSESSOR, UserRole.TEACHER]:
                print(f"\n🔹 {role_names[role]}账号:")
                role_accounts = [acc for acc in test_accounts if acc['role'] == role]
                for acc in role_accounts:
                    print(f"   用户名: {acc['username']:<12} 密码: {acc['password']:<12} 姓名: {acc['name']}")
            
            print("\n" + "=" * 60)
            print("🌟 所有账号创建完成！请使用上述账号进行测试。")
            
            return True
        
    except Exception as e:
        print(f"❌ 创建测试账号时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_test_accounts()
    sys.exit(0 if success else 1) 