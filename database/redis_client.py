# database/redis_client.py

import redis
import json
import os

class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0):
        # Use environment variables or defaults
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def set_json(self, key, value, expire=None):
        """Store a Python object as JSON string"""
        self.client.set(key, json.dumps(value))
        if expire:
            self.client.expire(key, expire)

    def get_json(self, key):
        """Get a JSON object by key"""
        value = self.client.get(key)
        return json.loads(value) if value else None

    def set(self, key, value, expire=None):
        """Set a string key"""
        self.client.set(key, value)
        if expire:
            self.client.expire(key, expire)

    def get(self, key):
        """Get a string key"""
        return self.client.get(key)

    def lpush(self, key, value):
        """Push to a Redis list (left)"""
        self.client.lpush(key, json.dumps(value))

    def lrange(self, key, start, end):
        """Return a list of JSON objects"""
        items = self.client.lrange(key, start, end)
        return [json.loads(item) for item in items]

    def publish(self, channel, data):
        """Publish a message (for real-time updates/pubsub)"""
        self.client.publish(channel, json.dumps(data))

    def subscribe(self, channel):
        """Subscribe to a channel"""
        pubsub = self.client.pubsub()
        pubsub.subscribe(channel)
        return pubsub

    def exists(self, key):
        return self.client.exists(key)

    def delete(self, key):
        self.client.delete(key)

# Singleton instance
redis_client = RedisClient()

# Example usage:
# redis_client.set_json('latest_alert', alert_dict)
# value = redis_client.get_json('latest_alert')
