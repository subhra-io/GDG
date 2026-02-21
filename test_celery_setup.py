"""Quick test script for Celery setup."""

import sys
import time
from src.workers.celery_app import celery_app
from src.workers.tasks import continuous_monitoring_task, scan_violations_task

def test_celery_connection():
    """Test Celery can connect to Redis."""
    print("🔍 Testing Celery connection to Redis...")
    try:
        inspect = celery_app.control.inspect()
        active = inspect.active()
        
        if active:
            print(f"✅ Connected! Found {len(active)} active worker(s)")
            for worker, tasks in active.items():
                print(f"   Worker: {worker}")
                print(f"   Active tasks: {len(tasks)}")
            return True
        else:
            print("⚠️  No active workers found. Start worker with:")
            print("   ./start_celery_worker.sh")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("   Make sure Redis is running: docker-compose up -d")
        return False


def test_trigger_scan():
    """Test triggering a scan task."""
    print("\n🚀 Testing manual scan trigger...")
    try:
        task = scan_violations_task.delay()
        print(f"✅ Task queued! Task ID: {task.id}")
        print(f"   Status: {task.status}")
        
        # Wait a bit and check status
        print("   Waiting 3 seconds...")
        time.sleep(3)
        
        print(f"   Status after 3s: {task.status}")
        
        if task.status == "SUCCESS":
            print(f"   Result: {task.result}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to trigger scan: {e}")
        return False


def test_monitoring_task():
    """Test continuous monitoring task."""
    print("\n📊 Testing continuous monitoring task...")
    try:
        task = continuous_monitoring_task.delay()
        print(f"✅ Monitoring task queued! Task ID: {task.id}")
        print(f"   Status: {task.status}")
        
        # Wait and check status
        print("   Waiting 5 seconds...")
        time.sleep(5)
        
        print(f"   Status after 5s: {task.status}")
        
        if task.status == "SUCCESS":
            print(f"   Result: {task.result}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to trigger monitoring: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Celery Setup Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: Connection
    results.append(("Connection", test_celery_connection()))
    
    if not results[0][1]:
        print("\n❌ Cannot proceed without Celery worker running")
        print("   Start worker: ./start_celery_worker.sh")
        sys.exit(1)
    
    # Test 2: Manual scan
    results.append(("Manual Scan", test_trigger_scan()))
    
    # Test 3: Monitoring task
    results.append(("Monitoring Task", test_monitoring_task()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Celery is working correctly.")
        print("\n📝 Next steps:")
        print("   1. Start Celery Beat: ./start_celery_beat.sh")
        print("   2. Check monitoring status: curl http://localhost:8000/api/v1/monitoring/status")
        print("   3. Add MonitoringStatus component to frontend")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
