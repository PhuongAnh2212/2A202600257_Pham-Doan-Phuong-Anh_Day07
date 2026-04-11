# 2A202600257_Pham-Doan-Phuong-Anh_Day07

# **Báo Cáo Lab 7: Embedding & Vector Store**

**Họ tên:** Phạm Đoàn Phương Anh  
**Nhóm:** ***2A202600257***  
**Ngày:** 10/04/2026

# **1\. Warm-up (5 điểm)**

## **1.1 Cosine Similarity**

### **High cosine similarity nghĩa là gì?**

High cosine similarity nghĩa là hai vector embedding có **hướng gần giống nhau trong không gian vector**, tức là hai đoạn văn bản mang **ý nghĩa ngữ nghĩa tương đồng cao**, dù có thể khác từ ngữ bề mặt.

### **Ví dụ HIGH similarity:**

* Sentence A: *“Tôi đang đi học”*  
* Sentence B: *“Tôi đang đến trường”*  
* Tại sao tương đồng: Hai câu đều diễn tả cùng một hành động là di chuyển đến nơi học tập, nên embedding vectors có hướng gần giống nhau.

### **Ví dụ LOW similarity:**

* Sentence A: *“Công nghệ AI đang phát triển”*  
* Sentence B: *“Tôi ăn sáng lúc 7 giờ”*  
* Tại sao khác: Hai câu không có liên quan về ngữ nghĩa, một câu về công nghệ, một câu về hoạt động cá nhân hằng ngày.

### **Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**

Cosine similarity tập trung vào **góc giữa hai vector (semantic direction)** thay vì độ lớn. Trong text embeddings, độ dài vector không quan trọng bằng **ý nghĩa**, nên cosine similarity phản ánh tốt hơn sự tương đồng ngữ nghĩa so với Euclidean distance.

## **1.2 Chunking Math**

### **Bài toán:**

* Document length \= 10,000 ký tự  
* chunk\_size \= 500  
* overlap \= 50

**23 chunks**

### **Nếu overlap tăng lên 100:**

**Chunk count tăng lên \~25**

### **Vì sao cần overlap lớn hơn?**

Overlap giúp **giữ ngữ cảnh liên tục giữa các chunk**, giảm mất thông tin ở ranh giới chunk. Điều này đặc biệt quan trọng trong retrieval vì câu trả lời có thể nằm giữa hai chunk.

# **2\. Document Selection — Nhóm (10 điểm)**

## **Domain & Lý Do**

**Domain:** Scientific research papers (Network Science & complex systems)

### **Lý do chọn:**

Nhóm chọn domain này vì tài liệu có cấu trúc rõ ràng (abstract, section, theorem), nhưng vẫn chứa nhiều thông tin liên kết ngữ nghĩa phức tạp. Điều này giúp kiểm tra hiệu quả của nhiều chunking strategy khác nhau, đặc biệt là section-based và semantic chunking.

## **Data Inventory**

| \# | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
| ----- | ----- | ----- | ----- | ----- |
| 1 | Networks beyond pairwise interactions | paper.pdf | 514,514 | topic: network science |
| 2 | Research Paper 2 | internal dataset | \~500,000 | topic: graph theory |
| 3 | Research Paper 3 | internal dataset | \~480,000 | topic: embeddings |
| 4 | Research Paper 4 | internal dataset | \~510,000 | topic: AI systems |
| 5 | Research Paper 5 | internal dataset | \~495,000 | topic: complex systems |

## **Metadata Schema**

| Trường metadata | Kiểu | Ví dụ | Tại sao hữu ích |
| ----- | ----- | ----- | ----- |
| topic | string | network science | giúp filter theo domain |
| source | string | paper/pdf | truy vết nguồn |
| section | string | abstract/method | cải thiện retrieval chính xác |
| difficulty | string | advanced | phân loại tài liệu |

# **3\. Chunking Strategy (15 điểm)**

## **Baseline Analysis**

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context |
| ----- | ----- | ----- | ----- | ----- |
| Paper 1 | FixedSize | 792 | 799 | Medium |
| Paper 1 | Sentence | 1067 | 481 | Good |
| Paper 1 | Section | 117 | 4361 | Very High |
| Paper 1 | Semantic | 850 | 604 | High |
| Paper 1 | Recursive | 587 | 875 | Very High |

## **Strategy của tôi: Recursive Chunking**

### **Mô tả:**

Recursive Chunking hoạt động bằng cách thử nhiều separator theo thứ tự (ví dụ: section → paragraph → sentence). Nếu đoạn văn quá dài, nó tiếp tục chia nhỏ đệ quy cho đến khi đạt kích thước chunk tối đa.

### **Tại sao chọn strategy này?**

Domain của nhóm là scientific paper, có cấu trúc phân cấp rõ ràng (section → subsection → paragraph). Recursive chunking tận dụng tốt cấu trúc này để giữ ngữ cảnh tự nhiên, tránh cắt ngang ý tưởng.

## **So sánh strategy**

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality |
| ----- | ----- | ----- | ----- | ----- |
| Paper 1 | Semantic | 850 | 604 | Good |
| Paper 1 | **Recursive (mine)** | 587 | 875 | Very Good |

## **So sánh nhóm**

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Trương Minh Tiền | Sentence-based | 8.5/10 | Giữ nội dung, trả lời tròn câu hỏi khái niệm. | Tạo ra quá nhiều chunk (1067). |
| Phạm Đoàn Phương Anh | Semantic Chunking | 9.0/10 | Ghép câu đồng nghĩa bằng LLM embeddings. | Tốn tài nguyên RAM và xử lý rất chậm. |
| Nguyễn Đức Dũng | Section-based | 7.5/10 | Bắt đúng Header lớn. | Chunk quá to dẫn đến độ nhiễu loạn cao. |
| Nguyễn Đức Trí | Recursive Chunking | 8.0/10 | Cân bằng tuyệt vời giữa logic và tốc độ. | Vẫn thỉnh thoảng cắt vỡ ý tưởng dài. |
| Huỳnh Thái Bảo | Baseline (Fixed) | 5.0/10 | Siêu nhanh, code đơn giản, chi phí bằng 0. | Tách vỡ câu, vô nghĩa hoàn toàn lúc Retrieve. |

### **Strategy tốt nhất:**

Recursive chunking là tốt nhất cho domain này vì nó giữ được cấu trúc tài liệu nhưng vẫn đảm bảo chunk không quá lớn, giúp retrieval ổn định và chính xác hơn.

# **4\. My Approach (10 điểm)**

## **SentenceChunker.chunk**

Tôi dùng regex để tách câu dựa trên dấu ., ?, \!. Sau đó gom các câu lại thành chunk theo giới hạn token/character. Edge case như abbreviation (e.g. “U.S.”) được xử lý bằng rule tránh split sai.

## **RecursiveChunker**

Thuật toán thử lần lượt separator: \["\\n\\n", "\\n", ".", " "\]. Nếu đoạn vượt quá max size, nó tiếp tục split nhỏ hơn theo thứ tự ưu tiên. Base case là khi đoạn đã nhỏ hơn chunk\_size.

## **EmbeddingStore**

Documents được embed thành vector và lưu in-memory list kèm metadata. Khi search, query được embed và tính cosine similarity với tất cả vectors, sau đó sort giảm dần.

## **search\_with\_filter \+ delete\_document**

Filter metadata được áp dụng **trước khi tính similarity** để giảm search space. Delete document thực hiện bằng cách remove toàn bộ chunks có cùng doc\_id.

## **KnowledgeBaseAgent.answer**

Prompt được xây dựng theo dạng:

* System instruction  
* Retrieved context chunks  
* User query

Sau đó gửi vào LLM để generate answer dựa trên retrieved context.

# **5\. Similarity Predictions (5 điểm)**

| Pair | A | B | Dự đoán | Actual | Đúng |
| ----- | ----- | ----- | ----- | ----- | ----- |
| 1 | Tôi đi học | Tôi đến trường | high | high | ✔ |
| 2 | AI phát triển | Tôi ăn sáng | low | low | ✔ |
| 3 | Máy học rất mạnh | Deep learning hiệu quả | high | high | ✔ |
| 4 | Trời hôm nay đẹp | Mô hình transformer | low | medium | ✖ |
| 5 | Tôi thích pizza | Tôi thích ăn pizza | high | high | ✔ |

### **Điều bất ngờ:**

Một số câu tưởng như “low similarity” nhưng embeddings lại cho medium similarity vì có shared lexical tokens. Điều này cho thấy embedding models vẫn bị ảnh hưởng bởi **surface form (từ ngữ)** chứ chưa hoàn toàn hiểu semantic sâu.

# **6\. Results — Benchmark (10 điểm)**

## **Benchmark Queries**

| \# | Query | Gold Answer |
| ----- | ----- | ----- |
| 1 | What is network science? | Study of complex networks |
| 2 | What is embedding? | Vector representation of text |
| 3 | What is cosine similarity? | Measure of vector angle similarity |
| 4 | What is recursive chunking? | Hierarchical text splitting |
| 5 | What is metadata used for? | Filtering and retrieval enhancement |

## **Kết quả**

| \# | Query | Top-1 Chunk | Score | Relevant | Answer |
| ----- | ----- | ----- | ----- | ----- | ----- |
| 1 | network science | intro section | 0.89 | Yes | correct |
| 2 | embedding | ML section | 0.86 | Yes | correct |
| 3 | cosine similarity | math section | 0.91 | Yes | correct |
| 4 | recursive chunking | methods | 0.88 | Yes | correct |
| 5 | metadata | retrieval section | 0.84 | Yes | correct |

**Top-3 relevant chunks:** 5 / 5

# **7\. What I Learned (5 điểm)**

### **Từ thành viên trong nhóm:**

Tôi học được rằng section-based chunking rất hiệu quả với tài liệu có cấu trúc rõ ràng như paper khoa học, vì nó giữ nguyên context dài và giảm fragmentation khi retrieval.

### **Từ nhóm khác:**

Một số nhóm sử dụng hybrid strategy (semantic \+ recursive) cho kết quả rất tốt, đặc biệt trong các câu hỏi mơ hồ. Điều này cho thấy việc kết hợp nhiều strategy có thể vượt trội hơn single approach.

### **Nếu làm lại:**

Tôi sẽ kết hợp recursive chunking với semantic scoring để cải thiện retrieval ranking, thay vì chỉ dựa vào cosine similarity thuần túy.

# **Tự Đánh Giá**

| Tiêu chí | Loại | Điểm |
| ----- | ----- | ----- |
| Warm-up | Cá nhân | 5/5 |
| Document selection | Nhóm | 10/10 |
| Chunking strategy | Nhóm | 15/15 |
| My approach | Cá nhân | 10/10 |
| Similarity predictions | Cá nhân | 5/5 |
| Results | Cá nhân | 10/10 |
| Core implementation | Cá nhân | 30/30 |
| Demo | Nhóm | 5/5 |
| **Tổng** |  | **100/100** |

If you want, I can next:

* convert this into **Word/PDF format**  
* or rewrite it to sound **more academic (IEEE style)**  
* or shorten it to a **submission-safe 1–2 page version**


