import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

class ConversationDB:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Establish connection to PostgreSQL database"""
        try:
            database_url = "postgresql://superuser:password@127.0.0.1:5432/orakulum"#s.getenv('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL not found in environment variables")
            
            self.connection = psycopg2.connect(database_url)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("Successfully connected to PostgreSQL database")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    
    def commit(self):
        """Commit transaction"""
        if self.connection:
            self.connection.commit()
    
    def rollback(self):
        """Rollback transaction"""
        if self.connection:
            self.connection.rollback()

    # CONVERSATIONS TABLE CRUD OPERATIONS
    
    def create_conversation(self, title: str = None) -> int:
        """Create a new conversation and return its ID"""
        query = """
        INSERT INTO conversations (title)
        VALUES (%s)
        RETURNING id
        """
        self.cursor.execute(query, (title,))
        conversation_id = self.cursor.fetchone()['id']
        self.commit()
        return conversation_id
    
    def get_conversation(self, conversation_id: int) -> Optional[Dict]:
        """Get a conversation by ID"""
        query = "SELECT * FROM conversations WHERE id = %s"
        self.cursor.execute(query, (conversation_id,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def get_all_conversations(self) -> List[Dict]:
        """Get all conversations"""
        query = "SELECT * FROM conversations ORDER BY created_at DESC"
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_conversation(self, conversation_id: int, title: str = None) -> bool:
        """Update a conversation"""
        query = "UPDATE conversations SET title = %s WHERE id = %s"
        self.cursor.execute(query, (title, conversation_id))
        self.commit()
        return self.cursor.rowcount > 0
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation (cascades to related tables)"""
        query = "DELETE FROM conversations WHERE id = %s"
        self.cursor.execute(query, (conversation_id,))
        self.commit()
        return self.cursor.rowcount > 0

    # CONVERSATION_PARTS TABLE CRUD OPERATIONS
    
    def create_conversation_part(self, 
                                conversation_id: int, 
                                author: str, 
                                tags: List[str] = None,
                                prompt: str = None,
                                content_type: str = 'text',
                                content: str = None,
                                content_json: Dict = None) -> int:
        """Create a new conversation part and return its ID"""
        if tags is None:
            tags = []
        
        query = """
        INSERT INTO conversation_parts 
        (conversation_id, author, tags, prompt, content_type, content, content_json)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        # Convert content_json to JSON string if provided
        json_content = json.dumps(content_json) if content_json else None
        
        self.cursor.execute(query, (
            conversation_id, author, tags, prompt, content_type, content, json_content
        ))
        part_id = self.cursor.fetchone()['id']
        self.commit()
        return part_id
    
    def get_conversation_part(self, part_id: int) -> Optional[Dict]:
        """Get a conversation part by ID"""
        query = "SELECT * FROM conversation_parts WHERE id = %s"
        self.cursor.execute(query, (part_id,))
        result = self.cursor.fetchone()
        if result:
            data = dict(result)
            # Parse JSON content if it exists
            if data['content_json']:
                data['content_json'] = json.loads(data['content_json'])
            return data
        return None
    
    def get_conversation_parts(self, conversation_id: int) -> List[Dict]:
        """Get all parts for a conversation"""
        query = """
        SELECT * FROM conversation_parts 
        WHERE conversation_id = %s 
        ORDER BY created_at ASC
        """
        self.cursor.execute(query, (conversation_id,))
        results = []
        for row in self.cursor.fetchall():
            data = dict(row)
            # Parse JSON content if it exists
            if data['content_json']:
                data['content_json'] = json.loads(data['content_json'])
            results.append(data)
        return results
    
    def update_conversation_part(self, 
                                part_id: int,
                                author: str = None,
                                tags: List[str] = None,
                                prompt: str = None,
                                content_type: str = None,
                                content: str = None,
                                content_json: Dict = None) -> bool:
        """Update a conversation part"""
        # Build dynamic query
        updates = []
        values = []
        
        if author is not None:
            updates.append("author = %s")
            values.append(author)
        if tags is not None:
            updates.append("tags = %s")
            values.append(tags)
        if prompt is not None:
            updates.append("prompt = %s")
            values.append(prompt)
        if content_type is not None:
            updates.append("content_type = %s")
            values.append(content_type)
        if content is not None:
            updates.append("content = %s")
            values.append(content)
        if content_json is not None:
            updates.append("content_json = %s")
            values.append(json.dumps(content_json))
        
        if not updates:
            return False
        
        values.append(part_id)
        query = f"UPDATE conversation_parts SET {', '.join(updates)} WHERE id = %s"
        
        self.cursor.execute(query, values)
        self.commit()
        return self.cursor.rowcount > 0
    
    def delete_conversation_part(self, part_id: int) -> bool:
        """Delete a conversation part"""
        query = "DELETE FROM conversation_parts WHERE id = %s"
        self.cursor.execute(query, (part_id,))
        self.commit()
        return self.cursor.rowcount > 0

    # CONVERSATION_EDGES TABLE CRUD OPERATIONS
    
    def create_conversation_edge(self,
                                conversation_id: int,
                                src_part_id: int,
                                dst_part_id: int,
                                label: str = None,
                                ord: int = 0,
                                weight: float = 0) -> int:
        """Create a new conversation edge and return its ID"""
        query = """
        INSERT INTO conversation_edges 
        (conversation_id, src_part_id, dst_part_id, label, ord, weight)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        self.cursor.execute(query, (
            conversation_id, src_part_id, dst_part_id, label, ord, weight
        ))
        edge_id = self.cursor.fetchone()['id']
        self.commit()
        return edge_id
    
    def get_conversation_edge(self, edge_id: int) -> Optional[Dict]:
        """Get a conversation edge by ID"""
        query = "SELECT * FROM conversation_edges WHERE id = %s"
        self.cursor.execute(query, (edge_id,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def get_conversation_edges(self, conversation_id: int) -> List[Dict]:
        """Get all edges for a conversation"""
        query = """
        SELECT * FROM conversation_edges 
        WHERE conversation_id = %s 
        ORDER BY ord ASC, created_at ASC
        """
        self.cursor.execute(query, (conversation_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_edges_from_part(self, src_part_id: int) -> List[Dict]:
        """Get all edges originating from a specific part"""
        query = """
        SELECT * FROM conversation_edges 
        WHERE src_part_id = %s 
        ORDER BY ord ASC
        """
        self.cursor.execute(query, (src_part_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_edges_to_part(self, dst_part_id: int) -> List[Dict]:
        """Get all edges pointing to a specific part"""
        query = """
        SELECT * FROM conversation_edges 
        WHERE dst_part_id = %s 
        ORDER BY ord ASC
        """
        self.cursor.execute(query, (dst_part_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_conversation_edge(self,
                                edge_id: int,
                                label: str = None,
                                ord: int = None,
                                weight: float = None) -> bool:
        """Update a conversation edge"""
        updates = []
        values = []
        
        if label is not None:
            updates.append("label = %s")
            values.append(label)
        if ord is not None:
            updates.append("ord = %s")
            values.append(ord)
        if weight is not None:
            updates.append("weight = %s")
            values.append(weight)
        
        if not updates:
            return False
        
        values.append(edge_id)
        query = f"UPDATE conversation_edges SET {', '.join(updates)} WHERE id = %s"
        
        self.cursor.execute(query, values)
        self.commit()
        return self.cursor.rowcount > 0
    
    def delete_conversation_edge(self, edge_id: int) -> bool:
        """Delete a conversation edge"""
        query = "DELETE FROM conversation_edges WHERE id = %s"
        self.cursor.execute(query, (edge_id,))
        self.commit()
        return self.cursor.rowcount > 0

    # CONVERSATION_ROOT TABLE CRUD OPERATIONS
    
    def create_conversation_root(self,
                                conversation_id: int,
                                autor: str,
                                type: str,
                                json_data: Dict = None,
                                text_data: str = None) -> int:
        """Create a new conversation root and return its ID"""
        query = """
        INSERT INTO conversation_root 
        (conversation_id, autor, type, json_data, text_data)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """
        
        json_content = json.dumps(json_data) if json_data else None
        
        self.cursor.execute(query, (
            conversation_id, autor, type, json_content, text_data
        ))
        root_id = self.cursor.fetchone()['id']
        self.commit()
        return root_id
    
    def get_conversation_root(self, root_id: int) -> Optional[Dict]:
        """Get a conversation root by ID"""
        query = "SELECT * FROM conversation_root WHERE id = %s"
        self.cursor.execute(query, (root_id,))
        result = self.cursor.fetchone()
        if result:
            data = dict(result)
            # Parse JSON data if it exists
            if data['json_data']:
                data['json_data'] = json.loads(data['json_data'])
            return data
        return None
    
    def get_conversation_roots(self, conversation_id: int) -> List[Dict]:
        """Get all roots for a conversation"""
        query = """
        SELECT * FROM conversation_root 
        WHERE conversation_id = %s 
        ORDER BY id ASC
        """
        self.cursor.execute(query, (conversation_id,))
        results = []
        for row in self.cursor.fetchall():
            data = dict(row)
            # Parse JSON data if it exists
            if data['json_data']:
                data['json_data'] = json.loads(data['json_data'])
            results.append(data)
        return results
    
    def update_conversation_root(self,
                                root_id: int,
                                autor: str = None,
                                type: str = None,
                                json_data: Dict = None,
                                text_data: str = None) -> bool:
        """Update a conversation root"""
        updates = []
        values = []
        
        if autor is not None:
            updates.append("autor = %s")
            values.append(autor)
        if type is not None:
            updates.append("type = %s")
            values.append(type)
        if json_data is not None:
            updates.append("json_data = %s")
            values.append(json.dumps(json_data))
        if text_data is not None:
            updates.append("text_data = %s")
            values.append(text_data)
        
        if not updates:
            return False
        
        values.append(root_id)
        query = f"UPDATE conversation_root SET {', '.join(updates)} WHERE id = %s"
        
        self.cursor.execute(query, values)
        self.commit()
        return self.cursor.rowcount > 0
    
    def delete_conversation_root(self, root_id: int) -> bool:
        """Delete a conversation root"""
        query = "DELETE FROM conversation_root WHERE id = %s"
        self.cursor.execute(query, (root_id,))
        self.commit()
        return self.cursor.rowcount > 0

    # UTILITY METHODS
    
    def get_conversation_with_parts(self, conversation_id: int) -> Optional[Dict]:
        """Get a conversation with all its parts and edges"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        conversation['parts'] = self.get_conversation_parts(conversation_id)
        conversation['edges'] = self.get_conversation_edges(conversation_id)
        conversation['roots'] = self.get_conversation_roots(conversation_id)
        
        return conversation
    
    def search_conversations(self, title_pattern: str = None) -> List[Dict]:
        """Search conversations by title pattern"""
        if title_pattern:
            query = "SELECT * FROM conversations WHERE title ILIKE %s ORDER BY created_at DESC"
            self.cursor.execute(query, (f"%{title_pattern}%",))
        else:
            query = "SELECT * FROM conversations ORDER BY created_at DESC"
            self.cursor.execute(query)
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def search_parts_by_tags(self, tags: List[str], conversation_id: int = None) -> List[Dict]:
        """Search conversation parts by tags"""
        if conversation_id:
            query = """
            SELECT * FROM conversation_parts 
            WHERE conversation_id = %s AND tags && %s 
            ORDER BY created_at ASC
            """
            self.cursor.execute(query, (conversation_id, tags))
        else:
            query = """
            SELECT * FROM conversation_parts 
            WHERE tags && %s 
            ORDER BY created_at ASC
            """
            self.cursor.execute(query, (tags,))
        
        results = []
        for row in self.cursor.fetchall():
            data = dict(row)
            if data['content_json']:
                data['content_json'] = json.loads(data['content_json'])
            results.append(data)
        return results


# Example usage and testing functions
def test_database_operations():
    """Test function to demonstrate database operations"""
    with ConversationDB() as db:
        # Create a conversation
        conv_id = db.create_conversation("Test Conversation")
        print(f"Created conversation with ID: {conv_id}")
        
        # Create conversation parts
        part1_id = db.create_conversation_part(
            conversation_id=conv_id,
            author="user",
            tags=["question", "general"],
            content_type="text",
            content="Hello, how are you?"
        )
        
        part2_id = db.create_conversation_part(
            conversation_id=conv_id,
            author="assistant",
            tags=["response", "helpful"],
            content_type="text",
            content="I'm doing well, thank you for asking!"
        )
        
        # Create an edge between parts
        edge_id = db.create_conversation_edge(
            conversation_id=conv_id,
            src_part_id=part1_id,
            dst_part_id=part2_id,
            label="response",
            ord=1
        )
        
        # Create a conversation root
        root_id = db.create_conversation_root(
            conversation_id=conv_id,
            autor="system",
            type="initialization",
            json_data={"version": "1.0", "model": "gpt-4"}
        )
        
        # Retrieve full conversation
        full_conversation = db.get_conversation_with_parts(conv_id)
        print(f"Full conversation: {json.dumps(full_conversation, indent=2, default=str)}")
        
        # Clean up
        db.delete_conversation(conv_id)
        print("Test conversation deleted")


if __name__ == "__main__":
    # Run test if script is executed directly
    test_database_operations()
