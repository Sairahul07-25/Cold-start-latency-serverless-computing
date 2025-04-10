import time
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import queue
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictiveResourceManager:
    def __init__(self, window_size=24, threshold=0.6):
        self.window_size = window_size
        self.threshold = threshold
        self.invocation_history = defaultdict(list)
        self.resource_pool = queue.Queue()
        self.warm_containers = set()
        
    def record_invocation(self, function_name, timestamp):
        self.invocation_history[function_name].append(timestamp)
        
    def predict_demand(self, function_name, current_time):
        if not self.invocation_history[function_name]:
            return False
            
        recent_invocations = [
            t for t in self.invocation_history[function_name]
            if current_time - timedelta(hours=self.window_size) <= t <= current_time
        ]
        
        if not recent_invocations:
            return False
            
        current_hour = current_time.hour
        similar_hour_invocations = [
            t for t in recent_invocations
            if abs(t.hour - current_hour) <= 1
        ]
        
        probability = len(similar_hour_invocations) / len(recent_invocations)
        return probability >= self.threshold
        
    def pre_warm_container(self, function_name):
        if function_name not in self.warm_containers:
            # Pre-warm initialization
            time.sleep(0.1)
            self.warm_containers.add(function_name)
            logger.info(f"Pre-warmed container for {function_name}")
            
    def get_container(self, function_name):
        return function_name in self.warm_containers

class ServerlessFunction:
    def __init__(self, name, resource_manager=None):
        self.name = name
        self.resource_manager = resource_manager
        
        if resource_manager:
            self.resource_manager.pre_warm_container(self.name)
        
    def cold_start_execution(self, input_data):
        start_time = time.time()
        
        time.sleep(0.5) 
        
        result = self.process_data(input_data)
        
        end_time = time.time()
        return result, round(end_time - start_time, 3)
        
    def optimized_execution(self, input_data):
        start_time = time.time()
        
        current_time = datetime.now()
        self.resource_manager.record_invocation(self.name, current_time)
        
        if self.resource_manager.get_container(self.name):
            time.sleep(0.1)
        else:
            time.sleep(0.5)
            self.resource_manager.pre_warm_container(self.name)
            
        result = self.process_data(input_data)
        
        end_time = time.time()
        return result, round(end_time - start_time, 3)
        
    def process_data(self, input_data):
        return {"processed": input_data}

def benchmark_comparison():
    resource_manager = PredictiveResourceManager()
    function = ServerlessFunction("test_function", resource_manager)
    
    test_data = {"data": "sample"}
    iterations = 10
    
    traditional_latencies = []
    logger.info("Testing traditional cold start approach...")
    for i in range(iterations):
        _, latency = function.cold_start_execution(test_data)
        traditional_latencies.append(latency)
        time.sleep(0.1)
        
    prp_latencies = []
    logger.info("Testing PRP-optimized approach...")
    for i in range(iterations):
        _, latency = function.optimized_execution(test_data)
        prp_latencies.append(latency)
        time.sleep(0.1)
        
    traditional_avg = round(np.mean(traditional_latencies), 3)
    traditional_std = round(np.std(traditional_latencies), 3)
    prp_avg = round(np.mean(prp_latencies), 3)
    prp_std = round(np.std(prp_latencies), 3)
    
    improvement = round(((traditional_avg - prp_avg) / traditional_avg) * 100, 3)
    
    results = {
        "traditional": {
            "average_latency": traditional_avg,
            "std_dev": traditional_std,
            "raw_latencies": traditional_latencies
        },
        "prp_optimized": {
            "average_latency": prp_avg,
            "std_dev": prp_std,
            "raw_latencies": prp_latencies
        },
        "improvement_percentage": improvement
    }
    
    return results

if __name__ == "__main__":
    results = benchmark_comparison()
    print(json.dumps(results, indent=2))