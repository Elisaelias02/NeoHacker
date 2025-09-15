#!/usr/bin/env python3
"""
NeonSec Hacker Blog Backend API Testing Suite
Tests all backend endpoints with realistic hacker-themed data
"""

import requests
import json
import sys
import os
from datetime import datetime
import time

# Backend URL from environment variable with fallback
BASE_URL = os.environ.get('BACKEND_URL', 'http://localhost:8001') + '/api'

class NeonSecAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.created_posts = []
        self.created_comments = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_api_root(self):
        """Test the root API endpoint"""
        self.log("Testing API root endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ API Root: {data}")
                return True
            else:
                self.log(f"❌ API Root failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ API Root exception: {str(e)}", "ERROR")
            return False
    
    def test_create_posts(self):
        """Test creating posts with hacker-themed content"""
        self.log("Testing POST /api/posts - Creating hacker-themed posts...")
        
        test_posts = [
            {
                "title": "Advanced OSINT Techniques for Red Team Operations",
                "content": "In this post, we'll explore advanced Open Source Intelligence gathering techniques that can be leveraged during red team engagements. We'll cover social media reconnaissance, domain enumeration, and metadata analysis.",
                "tags": ["osint", "redteam", "reconnaissance"],
                "author": "CyberNinja"
            },
            {
                "title": "Web Application Penetration Testing Methodology",
                "content": "A comprehensive guide to web application security testing covering OWASP Top 10, SQL injection, XSS, and authentication bypass techniques. Includes practical examples and tool usage.",
                "tags": ["web", "pentesting", "owasp"],
                "author": "WebHacker"
            },
            {
                "title": "Malware Analysis with Reverse Engineering",
                "content": "Deep dive into malware analysis techniques using static and dynamic analysis. We'll examine PE file structure, unpacking techniques, and behavioral analysis in sandboxed environments.",
                "tags": ["malware", "reverse-engineering", "forensics"],
                "author": "MalwareHunter"
            },
            {
                "title": "Blue Team Defense Strategies Against APTs",
                "content": "Effective defense strategies against Advanced Persistent Threats. Covering threat hunting, incident response, and security monitoring using SIEM and EDR solutions.",
                "tags": ["blueteam", "defense", "apt"],
                "author": "DefenseExpert"
            }
        ]
        
        success_count = 0
        for i, post_data in enumerate(test_posts):
            try:
                response = self.session.post(f"{self.base_url}/posts", json=post_data)
                if response.status_code == 200:
                    created_post = response.json()
                    self.created_posts.append(created_post)
                    self.log(f"✅ Created post {i+1}: '{created_post['title'][:50]}...' (ID: {created_post['id']})")
                    success_count += 1
                else:
                    self.log(f"❌ Failed to create post {i+1}: {response.status_code} - {response.text}", "ERROR")
            except Exception as e:
                self.log(f"❌ Exception creating post {i+1}: {str(e)}", "ERROR")
        
        self.log(f"Posts creation summary: {success_count}/{len(test_posts)} successful")
        return success_count == len(test_posts)
    
    def test_get_all_posts(self):
        """Test retrieving all posts"""
        self.log("Testing GET /api/posts - Retrieving all posts...")
        try:
            response = self.session.get(f"{self.base_url}/posts")
            if response.status_code == 200:
                posts = response.json()
                self.log(f"✅ Retrieved {len(posts)} posts")
                for post in posts[:3]:  # Show first 3 posts
                    self.log(f"   - {post['title']} by {post['author']} (tags: {', '.join(post['tags'])})")
                return True
            else:
                self.log(f"❌ Failed to get posts: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception getting posts: {str(e)}", "ERROR")
            return False
    
    def test_get_post_by_id(self):
        """Test retrieving specific post by ID"""
        if not self.created_posts:
            self.log("❌ No posts available for ID testing", "ERROR")
            return False
            
        self.log("Testing GET /api/posts/{post_id} - Retrieving specific post...")
        post_id = self.created_posts[0]['id']
        try:
            response = self.session.get(f"{self.base_url}/posts/{post_id}")
            if response.status_code == 200:
                post = response.json()
                self.log(f"✅ Retrieved post by ID: '{post['title']}' by {post['author']}")
                return True
            else:
                self.log(f"❌ Failed to get post by ID: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception getting post by ID: {str(e)}", "ERROR")
            return False
    
    def test_search_posts(self):
        """Test search functionality"""
        self.log("Testing GET /api/posts?search=OSINT - Search functionality...")
        try:
            response = self.session.get(f"{self.base_url}/posts?search=OSINT")
            if response.status_code == 200:
                posts = response.json()
                self.log(f"✅ Search for 'OSINT' returned {len(posts)} posts")
                for post in posts:
                    self.log(f"   - {post['title']} (matches in title/content/tags)")
                return True
            else:
                self.log(f"❌ Search failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception during search: {str(e)}", "ERROR")
            return False
    
    def test_filter_by_tag(self):
        """Test tag filtering"""
        self.log("Testing GET /api/posts?tag=pentesting - Tag filtering...")
        try:
            response = self.session.get(f"{self.base_url}/posts?tag=pentesting")
            if response.status_code == 200:
                posts = response.json()
                self.log(f"✅ Tag filter 'pentesting' returned {len(posts)} posts")
                for post in posts:
                    self.log(f"   - {post['title']} (tags: {', '.join(post['tags'])})")
                return True
            else:
                self.log(f"❌ Tag filtering failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception during tag filtering: {str(e)}", "ERROR")
            return False
    
    def test_create_comments(self):
        """Test creating comments for posts"""
        if not self.created_posts:
            self.log("❌ No posts available for comment testing", "ERROR")
            return False
            
        self.log("Testing POST /api/comments - Creating comments...")
        
        test_comments = [
            {
                "post_id": self.created_posts[0]['id'],
                "content": "Great article! The OSINT techniques you mentioned are really effective. I've used similar approaches in my red team engagements.",
                "author": "RedTeamLead"
            },
            {
                "post_id": self.created_posts[0]['id'],
                "content": "Thanks for sharing this. The social media reconnaissance part was particularly insightful. Any recommendations for automated tools?",
                "author": "InfoSecStudent"
            },
            {
                "post_id": self.created_posts[1]['id'],
                "content": "Excellent web pentesting guide! The OWASP coverage is comprehensive. Would love to see more on API security testing.",
                "author": "WebSecExpert"
            }
        ]
        
        success_count = 0
        for i, comment_data in enumerate(test_comments):
            try:
                response = self.session.post(f"{self.base_url}/comments", json=comment_data)
                if response.status_code == 200:
                    created_comment = response.json()
                    self.created_comments.append(created_comment)
                    self.log(f"✅ Created comment {i+1} by {created_comment['author']} (ID: {created_comment['id']})")
                    success_count += 1
                else:
                    self.log(f"❌ Failed to create comment {i+1}: {response.status_code} - {response.text}", "ERROR")
            except Exception as e:
                self.log(f"❌ Exception creating comment {i+1}: {str(e)}", "ERROR")
        
        self.log(f"Comments creation summary: {success_count}/{len(test_comments)} successful")
        return success_count == len(test_comments)
    
    def test_get_comments(self):
        """Test retrieving comments for posts"""
        if not self.created_posts:
            self.log("❌ No posts available for comment retrieval testing", "ERROR")
            return False
            
        self.log("Testing GET /api/comments/{post_id} - Retrieving comments...")
        post_id = self.created_posts[0]['id']
        try:
            response = self.session.get(f"{self.base_url}/comments/{post_id}")
            if response.status_code == 200:
                comments = response.json()
                self.log(f"✅ Retrieved {len(comments)} comments for post")
                for comment in comments:
                    self.log(f"   - {comment['author']}: {comment['content'][:50]}...")
                return True
            else:
                self.log(f"❌ Failed to get comments: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception getting comments: {str(e)}", "ERROR")
            return False
    
    def test_get_popular_tags(self):
        """Test retrieving popular tags"""
        self.log("Testing GET /api/tags - Retrieving popular tags...")
        try:
            response = self.session.get(f"{self.base_url}/tags")
            if response.status_code == 200:
                tags = response.json()
                self.log(f"✅ Retrieved {len(tags)} popular tags")
                for tag in tags[:10]:  # Show top 10 tags
                    self.log(f"   - #{tag['tag']}: {tag['count']} posts")
                return True
            else:
                self.log(f"❌ Failed to get tags: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception getting tags: {str(e)}", "ERROR")
            return False
    
    def test_delete_post(self):
        """Test deleting a post and its associated comments"""
        if not self.created_posts:
            self.log("❌ No posts available for deletion testing", "ERROR")
            return False
            
        self.log("Testing DELETE /api/posts/{post_id} - Deleting post...")
        post_to_delete = self.created_posts[-1]  # Delete the last created post
        post_id = post_to_delete['id']
        
        try:
            response = self.session.delete(f"{self.base_url}/posts/{post_id}")
            if response.status_code == 200:
                result = response.json()
                self.log(f"✅ Deleted post: '{post_to_delete['title'][:50]}...' - {result['message']}")
                
                # Verify post is actually deleted
                verify_response = self.session.get(f"{self.base_url}/posts/{post_id}")
                if verify_response.status_code == 404:
                    self.log("✅ Verified post deletion - post no longer exists")
                    return True
                else:
                    self.log("❌ Post deletion verification failed - post still exists", "ERROR")
                    return False
            else:
                self.log(f"❌ Failed to delete post: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception deleting post: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all API tests in sequence"""
        self.log("=" * 60)
        self.log("STARTING NEONSEC HACKER BLOG API TESTING SUITE")
        self.log("=" * 60)
        
        tests = [
            ("API Root", self.test_api_root),
            ("Create Posts", self.test_create_posts),
            ("Get All Posts", self.test_get_all_posts),
            ("Get Post by ID", self.test_get_post_by_id),
            ("Search Posts", self.test_search_posts),
            ("Filter by Tag", self.test_filter_by_tag),
            ("Create Comments", self.test_create_comments),
            ("Get Comments", self.test_get_comments),
            ("Get Popular Tags", self.test_get_popular_tags),
            ("Delete Post", self.test_delete_post)
        ]
        
        results = {}
        for test_name, test_func in tests:
            self.log(f"\n--- Running {test_name} Test ---")
            try:
                results[test_name] = test_func()
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                self.log(f"❌ {test_name} test failed with exception: {str(e)}", "ERROR")
                results[test_name] = False
        
        # Summary
        self.log("\n" + "=" * 60)
        self.log("TEST RESULTS SUMMARY")
        self.log("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name}: {status}")
            if result:
                passed += 1
        
        self.log(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED! NeonSec API is working correctly.")
            return True
        else:
            self.log(f"⚠️  {total-passed} tests failed. Check the logs above for details.")
            return False

if __name__ == "__main__":
    tester = NeonSecAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)