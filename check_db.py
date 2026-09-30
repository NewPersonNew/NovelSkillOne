# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# check_db.py
import sqlite3
import json
import os

def check_database(project_name="我的第一本小说"):
    db_path = f"./data/{project_name}/canon.db"
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print(f"\n📊 检查数据库: {project_name}")
    print("=" * 50)

    # 检查所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_names = [t['name'] for t in tables]
    print(f"已有表: {table_names}")

    # 1. facts 表
    if 'facts' in table_names:
        cursor.execute("SELECT COUNT(*) as cnt FROM facts")
        total = cursor.fetchone()['cnt']
        print(f"\n📋 facts 表总记录数: {total}")
        if total > 0:
            cursor.execute("SELECT * FROM facts ORDER BY id DESC LIMIT 20")
            rows = cursor.fetchall()
            print("最新20条事实:")
            for r in rows:
                print(f"  ID:{r['id']} | {r['entity']} → {r['attribute']} = {r['value']} (第{r['chapter']}章)")
        else:
            print("  (空)")
    else:
        print("⚠️ facts 表不存在")

    # 2. promises 表
    if 'promises' in table_names:
        cursor.execute("SELECT COUNT(*) as cnt FROM promises")
        total = cursor.fetchone()['cnt']
        print(f"\n📋 promises 表总记录数: {total}")
        if total > 0:
            cursor.execute("SELECT * FROM promises ORDER BY id DESC LIMIT 20")
            rows = cursor.fetchall()
            print("最新20条承诺:")
            for r in rows:
                status = r['status']
                resolved_info = f" (已回收于第{r['resolved_chapter']}章)" if r['resolved_chapter'] else ""
                print(f"  ID:{r['id']} | {r['description']} (埋于第{r['planted_chapter']}章, 状态:{status}){resolved_info}")
        else:
            print("  (空)")
    else:
        print("⚠️ promises 表不存在")

    # 3. characters 表
    if 'characters' in table_names:
        cursor.execute("SELECT COUNT(*) as cnt FROM characters")
        total = cursor.fetchone()['cnt']
        print(f"\n📋 characters 表总记录数: {total}")
        if total > 0:
            cursor.execute("SELECT name, profile, current_state, last_updated_chapter FROM characters LIMIT 20")
            rows = cursor.fetchall()
            print("角色信息:")
            for r in rows:
                profile = json.loads(r['profile']) if r['profile'] else {}
                state = json.loads(r['current_state']) if r['current_state'] else {}
                print(f"  {r['name']} | 性格: {profile.get('personality', '')[:30]} | 状态: {state.get('status', '')[:30]} | 更新于第{r['last_updated_chapter']}章")
        else:
            print("  (空)")
    else:
        print("⚠️ characters 表不存在")

    conn.close()

if __name__ == "__main__":
    import sys
    project = sys.argv[1] if len(sys.argv) > 1 else "我的第一本小说"
    check_database(project)