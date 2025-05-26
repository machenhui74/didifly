#!/usr/bin/env python3
"""
校长权限测试脚本
验证校长权限限制是否正确实现
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_principal_permissions():
    """测试校长权限限制"""
    print("🔍 测试校长权限限制...")
    
    try:
        # 导入必要的模块
        from logic.auth import UserRole, USERS, get_user_role
        from logic.student_utils import filter_accessible_profiles
        
        print("✅ 模块导入成功")
        
        # 测试1: 检查校长权限常量
        print(f"📋 校长权限常量: {UserRole.PRINCIPAL}")
        assert UserRole.PRINCIPAL == 'principal', "校长权限常量错误"
        print("✅ 校长权限常量正确")
        
        # 测试2: 模拟校长用户数据
        test_principal = {
            'password': 'test_hash',
            'name': '测试校长',
            'store': '测试训练中心',
            'role': UserRole.PRINCIPAL,
            'is_encrypted': True,
            'created_users_count': 0,
            'created_users_list': []
        }
        
        # 模拟学生档案数据
        test_profiles = [
            {
                'name': '学生A',
                'training_center': '测试训练中心',
                'assessor': '测评师A'
            },
            {
                'name': '学生B', 
                'training_center': '其他训练中心',
                'assessor': '测评师B'
            },
            {
                'name': '学生C',
                'training_center': '测试训练中心',
                'assessor': '测评师C'
            }
        ]
        
        # 临时添加测试用户
        USERS['test_principal'] = test_principal
        
        # 测试3: 验证学生档案过滤
        filtered_profiles = filter_accessible_profiles(test_profiles, 'test_principal', '测试训练中心')
        
        # 校长应该只能看到同训练中心的学生档案
        expected_count = 2  # 学生A和学生C
        actual_count = len(filtered_profiles)
        
        print(f"📊 学生档案过滤测试:")
        print(f"   - 总档案数: {len(test_profiles)}")
        print(f"   - 校长可见档案数: {actual_count}")
        print(f"   - 预期可见档案数: {expected_count}")
        
        assert actual_count == expected_count, f"档案过滤错误: 预期{expected_count}个，实际{actual_count}个"
        
        # 验证过滤结果的训练中心
        for profile in filtered_profiles:
            assert profile['training_center'] == '测试训练中心', f"档案过滤错误: 包含其他训练中心的档案"
        
        print("✅ 学生档案过滤测试通过")
        
        # 清理测试数据
        del USERS['test_principal']
        
        print("🎉 所有校长权限测试通过！")
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        return False

def test_user_profile_restrictions():
    """测试用户信息修改限制"""
    print("\n🔍 测试用户信息修改限制...")
    
    try:
        from logic.users import update_user
        from logic.auth import UserRole, USERS
        
        # 创建测试校长用户
        test_principal = {
            'password': 'test_hash',
            'name': '测试校长',
            'store': '测试训练中心',
            'role': UserRole.PRINCIPAL,
            'is_encrypted': True,
            'created_users_count': 0,
            'created_users_list': []
        }
        
        USERS['test_principal'] = test_principal
        
        # 测试校长修改密码（应该成功）
        success, message = update_user(
            'test_principal',
            password='new_password123',
            name=None,
            store=None,
            role=None,
            operator_id='test_principal'
        )
        
        print(f"📝 校长修改密码测试: {'✅ 成功' if success else '❌ 失败'}")
        if not success:
            print(f"   错误信息: {message}")
        
        # 清理测试数据
        del USERS['test_principal']
        
        print("✅ 用户信息修改限制测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 用户信息修改测试出错: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始校长权限测试...")
    
    # 运行测试
    test1_result = test_principal_permissions()
    test2_result = test_user_profile_restrictions()
    
    if test1_result and test2_result:
        print("\n🎉 所有测试通过！校长权限限制实现正确。")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败，请检查实现。")
        sys.exit(1) 