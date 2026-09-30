# -*- coding: utf-8 -*-
__author__ = "gezhaoqiang"
__date__ = "2026/8/28"

# memory/db_manager.py
import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, project_name: str, base_path: str = "./data"):
        self.project_path = os.path.join(base_path, project_name)
        os.makedirs(self.project_path, exist_ok=True)
        self.db_path = os.path.join(self.project_path, "canon.db")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # 返回字典形式
        self._init_tables()

    def _init_tables(self):
        cursor = self.conn.cursor()
        # 事实表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity TEXT NOT NULL,
                attribute TEXT NOT NULL,
                value TEXT,
                chapter INTEGER NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                source TEXT DEFAULT 'generated',
                UNIQUE(entity, attribute, value, chapter)  -- 防重复
            )
        ''')
        # 承诺表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                planted_chapter INTEGER NOT NULL,
                expected_chapter INTEGER,
                resolved_chapter INTEGER,
                status TEXT DEFAULT 'active',
                notes TEXT
            )
        ''')
        # 角色表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                name TEXT PRIMARY KEY,
                profile TEXT,  -- JSON 存储静态设定
                current_state TEXT, -- JSON 存储动态状态
                last_updated_chapter INTEGER,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # 创建索引加速查询
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_facts_entity ON facts(entity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_facts_chapter ON facts(chapter)')
        self.conn.commit()

    def insert_fact(self, entity: str, attribute: str, value: str, chapter: int, source: str = 'generated'):
        """插入一条事实（仅当不存在时）"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO facts (entity, attribute, value, chapter, source)
                VALUES (?, ?, ?, ?, ?)
            ''', (entity, attribute, value, chapter, source))
            self.conn.commit()
        except Exception as e:
            print(f"插入事实失败: {e}")

    def get_facts(self, entity: Optional[str] = None, chapter: Optional[int] = None, limit: int = 100) -> List[Dict]:
        """查询事实，支持按实体或章节过滤"""
        cursor = self.conn.cursor()
        sql = "SELECT * FROM facts WHERE 1=1"
        params = []
        if entity:
            sql += " AND entity = ?"
            params.append(entity)
        if chapter:
            sql += " AND chapter = ?"
            params.append(chapter)
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_facts_by_entity(self, entity: str) -> List[Dict]:
        """获取某个实体的所有事实（按时间正序）"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM facts WHERE entity = ? ORDER BY id ASC
        ''', (entity,))
        return [dict(row) for row in cursor.fetchall()]

    def upsert_promise(self, description: str, planted_chapter: int, expected_chapter: Optional[int] = None, status: str = 'active', notes: str = ''):
        """插入或更新承诺（按描述去重）"""
        cursor = self.conn.cursor()
        # 检查是否已存在
        cursor.execute('SELECT id FROM promises WHERE description = ?', (description,))
        existing = cursor.fetchone()
        if existing:
            cursor.execute('''
                UPDATE promises SET expected_chapter=?, status=?, notes=?
                WHERE id=?
            ''', (expected_chapter, status, notes, existing['id']))
        else:
            cursor.execute('''
                INSERT INTO promises (description, planted_chapter, expected_chapter, status, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (description, planted_chapter, expected_chapter, status, notes))
        self.conn.commit()

    def resolve_promise(self, promise_id: int, resolved_chapter: int):
        """将承诺标记为已回收"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE promises SET status='resolved', resolved_chapter=?
            WHERE id=?
        ''', (resolved_chapter, promise_id))
        self.conn.commit()

    def get_active_promises(self) -> List[Dict]:
        """获取所有活跃的承诺"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM promises WHERE status = "active" ORDER BY planted_chapter ASC')
        return [dict(row) for row in cursor.fetchall()]

    def upsert_character(self, name: str, profile: Dict = None, state: Dict = None, chapter: int = 0):
        """更新角色档案"""
        cursor = self.conn.cursor()
        profile_json = json.dumps(profile, ensure_ascii=False) if profile else '{}'
        state_json = json.dumps(state, ensure_ascii=False) if state else '{}'
        cursor.execute('''
            INSERT OR REPLACE INTO characters (name, profile, current_state, last_updated_chapter)
            VALUES (?, ?, ?, ?)
        ''', (name, profile_json, state_json, chapter))
        self.conn.commit()

    def get_character(self, name: str) -> Dict:
        """获取角色完整信息"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM characters WHERE name = ?', (name,))
        row = cursor.fetchone()
        if row:
            d = dict(row)
            d['profile'] = json.loads(d['profile']) if d['profile'] else {}
            d['current_state'] = json.loads(d['current_state']) if d['current_state'] else {}
            return d
        return {}

    def close(self):
        self.conn.close()