import time
import asyncio
import numpy as np
import httpx

API_BASE = "http://localhost:8000"

async def run_benchmark(num_requests: int = 50, concurrency: int = 5):
    print("==========================================================")
    print(" Running Enterprise Doc Intelligence Performance Benchmark")
    print(f" Requests: {num_requests} | Concurrency: {concurrency}")
    print("==========================================================")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Login to obtain token
        login_res = await client.post(
            f"{API_BASE}/auth/login",
            json={"email": "admin@example.com", "password": "AdminPass123!"}
        )
        if login_res.status_code != 200:
            print("Failed to authenticate:", login_res.text)
            return

        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # ----------------------------------------------------
        # Benchmark 1: API Endpoint Throughput (e.g. GET /documents)
        # ----------------------------------------------------
        print("\n[Phase 1] Benchmarking REST API Read Latency (/documents)...")
        latencies_api = []
        success_api = 0
        failed_api = 0

        sem = asyncio.Semaphore(concurrency)

        async def make_api_call():
            nonlocal success_api, failed_api
            async with sem:
                t0 = time.perf_counter()
                try:
                    res = await client.get(f"{API_BASE}/documents", headers=headers)
                    elapsed = (time.perf_counter() - t0) * 1000.0  # ms
                    if res.status_code == 200:
                        success_api += 1
                        latencies_api.append(elapsed)
                    else:
                        failed_api += 1
                except Exception:
                    failed_api += 1

        t_start = time.perf_counter()
        tasks = [make_api_call() for _ in range(num_requests)]
        await asyncio.gather(*tasks)
        total_time_api = time.perf_counter() - t_start

        # ----------------------------------------------------
        # Benchmark 2: Access-Aware RAG Retrieval Latency (/rag/query)
        # ----------------------------------------------------
        print("[Phase 2] Benchmarking Access-Aware RAG Vector Retrieval (/rag/query)...")
        latencies_rag = []
        success_rag = 0
        failed_rag = 0

        rag_queries = [
            "What is the remote work policy?",
            "What are the payment terms in the invoice?",
            "What are the termination notice requirements?",
            "What are the password security rules?"
        ]

        async def make_rag_call(idx):
            nonlocal success_rag, failed_rag
            q = rag_queries[idx % len(rag_queries)]
            async with sem:
                t0 = time.perf_counter()
                try:
                    res = await client.post(
                        f"{API_BASE}/rag/query",
                        headers=headers,
                        json={"query": q, "top_k": 4}
                    )
                    elapsed = (time.perf_counter() - t0) * 1000.0
                    if res.status_code == 200:
                        success_rag += 1
                        latencies_rag.append(elapsed)
                    else:
                        failed_rag += 1
                except Exception:
                    failed_rag += 1

        t_start_rag = time.perf_counter()
        tasks_rag = [make_rag_call(i) for i in range(min(num_requests, 30))]
        await asyncio.gather(*tasks_rag)
        total_time_rag = time.perf_counter() - t_start_rag

        # ----------------------------------------------------
        # Report Results
        # ----------------------------------------------------
        print("\n==========================================================")
        print(" PERFORMANCE BENCHMARK RESULTS")
        print("==========================================================")
        
        print("\n--- 1. REST API Endpoint (/documents) ---")
        print(f"Total Requests:       {num_requests}")
        print(f"Successful Requests:  {success_api}")
        print(f"Failed Requests:      {failed_api}")
        print(f"Total Duration:       {total_time_api:.2f} s")
        print(f"Requests / Second:    {num_requests / total_time_api:.2f} req/s")
        if latencies_api:
            print(f"p50 Latency:          {np.percentile(latencies_api, 50):.2f} ms")
            print(f"p95 Latency:          {np.percentile(latencies_api, 95):.2f} ms")
            print(f"p99 Latency:          {np.percentile(latencies_api, 99):.2f} ms")
            print(f"Min Latency:          {np.min(latencies_api):.2f} ms")
            print(f"Max Latency:          {np.max(latencies_api):.2f} ms")

        print("\n--- 2. Access-Aware RAG Vector Retrieval (/rag/query) ---")
        num_rag = len(tasks_rag)
        print(f"Total Queries:        {num_rag}")
        print(f"Successful Queries:   {success_rag}")
        print(f"Failed Queries:       {failed_rag}")
        print(f"Total Duration:       {total_time_rag:.2f} s")
        print(f"Queries / Second:     {num_rag / total_time_rag:.2f} req/s")
        if latencies_rag:
            print(f"p50 Latency:          {np.percentile(latencies_rag, 50):.2f} ms")
            print(f"p95 Latency:          {np.percentile(latencies_rag, 95):.2f} ms")
            print(f"p99 Latency:          {np.percentile(latencies_rag, 99):.2f} ms")
            print(f"Min Latency:          {np.min(latencies_rag):.2f} ms")
            print(f"Max Latency:          {np.max(latencies_rag):.2f} ms")
        print("==========================================================\n")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
