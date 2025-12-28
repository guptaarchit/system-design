# Design a File Downloader Library

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Library Architecture](#library-architecture)
4. [API Design](#api-design)
5. [Download Strategies](#download-strategies)
6. [Resume & Retry Logic](#resume--retry-logic)
7. [Progress Tracking](#progress-tracking)
8. [Error Handling](#error-handling)
9. [Performance Optimization](#performance-optimization)
10. [Security Considerations](#security-considerations)
11. [Testing Strategy](#testing-strategy)
12. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A robust file downloader library that supports resumable downloads, parallel chunk downloads, progress tracking, error handling, and various download strategies. The library must be easy to use, performant, and handle edge cases gracefully.

**Key Features:**
- Resumable downloads
- Parallel chunk downloads
- Progress callbacks
- Retry logic
- Pause/resume functionality
- Bandwidth throttling
- Download queue management
- Multiple protocol support (HTTP, HTTPS, FTP)

---

## Requirements

### Functional Requirements

1. **Download Management**
   - Download single files
   - Download multiple files (queue)
   - Pause/resume downloads
   - Cancel downloads

2. **Resume Support**
   - Resume interrupted downloads
   - Partial file handling
   - Range request support

3. **Progress Tracking**
   - Real-time progress updates
   - Speed calculation
   - ETA estimation

4. **Error Handling**
   - Network error retry
   - Timeout handling
   - Invalid URL handling

### Non-Functional Requirements

1. **Performance**
   - Fast download speeds
   - Low memory footprint
   - Efficient chunk management

2. **Reliability**
   - Handle network interruptions
   - Data integrity (checksums)
   - Atomic file writes

3. **Usability**
   - Simple API
   - Good error messages
   - Comprehensive documentation

---

## Library Architecture

### High-Level Design (HLD)

**1. Core Components**
- **FileDownloader**: Main downloader class
- **DownloadStrategy**: Strategy interface for different methods
- **ChunkDownloader**: Handles chunk-based downloads
- **ProgressTracker**: Tracks download progress
- **RetryManager**: Manages retry logic

**2. Supporting Components**
- **ConnectionManager**: Manages HTTP connections
- **StateManager**: Manages download state
- **QueueManager**: Manages download queue
- **BandwidthThrottler**: Throttles bandwidth

### Low-Level Design (LLD)

```python
# Core Components

class FileDownloader:
    """Main downloader class"""
    def __init__(self, config: DownloadConfig):
        self.config = config
        self.strategy = self._create_strategy(config.strategy_type)
        self.state_manager = StateManager(config.state_file)
        self.retry_manager = RetryManager(config.max_retries, config.backoff_factor)
        self.progress_tracker = ProgressTracker()
    
    def download(self, url: str, destination: str, callbacks: dict = None):
        # Load state if exists
        state = self.state_manager.load_state(url, destination)
        
        # Create download task
        task = DownloadTask(url, destination, state)
        
        # Execute with retry
        return self.retry_manager.execute(
            lambda: self.strategy.download(task, callbacks)
        )
    
    def pause(self, task_id: str):
        task = self.get_task(task_id)
        task.pause()
        self.state_manager.save_state(task)
    
    def resume(self, task_id: str):
        task = self.get_task(task_id)
        task.resume()
        return self.download(task.url, task.destination)
    
    def cancel(self, task_id: str):
        task = self.get_task(task_id)
        task.cancel()
        self.state_manager.delete_state(task)

class DownloadStrategy:
    """Strategy interface for different download methods"""
    def download(self, task: DownloadTask, callbacks: dict):
        raise NotImplementedError()

class SequentialDownloadStrategy(DownloadStrategy):
    """Sequential download strategy"""
    def download(self, task: DownloadTask, callbacks: dict):
        # Implementation
        pass

class ParallelChunkDownloadStrategy(DownloadStrategy):
    """Parallel chunk download strategy"""
    def download(self, task: DownloadTask, callbacks: dict):
        # Implementation
        pass

class ChunkDownloader:
    """Handles chunk-based downloads"""
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
    
    def download_chunk(self, url: str, start: int, end: int, chunk_id: int, 
                      destination: str):
        headers = {'Range': f'bytes={start}-{end}'}
        response = self.connection_manager.get(url, headers=headers, stream=True)
        
        chunk_file = f"{destination}.chunk{chunk_id}"
        with open(chunk_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return chunk_file
    
    def merge_chunks(self, destination: str, num_chunks: int):
        with open(destination, 'wb') as outfile:
            for i in range(num_chunks):
                chunk_file = f"{destination}.chunk{i}"
                with open(chunk_file, 'rb') as infile:
                    outfile.write(infile.read())
                os.remove(chunk_file)

class ProgressTracker:
    """Tracks download progress"""
    def __init__(self):
        self.total_size = 0
        self.downloaded = 0
        self.start_time = time.time()
        self.last_update_time = time.time()
        self.last_downloaded = 0
    
    def update(self, bytes_downloaded: int):
        self.downloaded = bytes_downloaded
        
        current_time = time.time()
        elapsed = current_time - self.start_time
        time_since_last_update = current_time - self.last_update_time
        
        # Calculate speed
        bytes_since_last_update = self.downloaded - self.last_downloaded
        if time_since_last_update > 0:
            speed = bytes_since_last_update / time_since_last_update
        else:
            speed = 0
        
        # Calculate ETA
        remaining_bytes = self.total_size - self.downloaded
        if speed > 0:
            eta_seconds = remaining_bytes / speed
        else:
            eta_seconds = 0
        
        # Calculate percentage
        percentage = (self.downloaded / self.total_size) * 100 if self.total_size > 0 else 0
        
        self.last_update_time = current_time
        self.last_downloaded = self.downloaded
        
        return {
            'downloaded': self.downloaded,
            'total': self.total_size,
            'percentage': percentage,
            'speed': speed,
            'eta_seconds': eta_seconds,
            'elapsed_seconds': elapsed
        }
    
    def get_progress(self) -> dict:
        return {
            'downloaded': self.downloaded,
            'total': self.total_size,
            'percentage': (self.downloaded / self.total_size) * 100 if self.total_size > 0 else 0
        }

class RetryManager:
    """Manages retry logic"""
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def execute(self, func, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except RetryableError as e:
                if attempt == self.max_retries - 1:
                    raise
                wait_time = self.backoff_factor ** attempt
                time.sleep(wait_time)
            except NonRetryableError:
                raise
    
    def should_retry(self, error: Exception) -> bool:
        return isinstance(error, RetryableError)
    
    def get_backoff_delay(self, attempt: int) -> float:
        return self.backoff_factor ** attempt
```

---

## Fault Tolerance

### Download Fault Tolerance

**1. Resume Capability**
- **State Persistence**: Save download state periodically
- **Metadata File**: Store metadata (downloaded bytes, URL, etc.)
- **Resume on Restart**: Resume from saved state
- **Partial File Handling**: Handle partial files correctly

**2. Network Failure Handling**
- **Retry Logic**: Retry with exponential backoff
- **Connection Timeout**: Handle connection timeouts
- **Partial Download**: Resume partial downloads
- **Error Recovery**: Recover from network errors

**3. Chunk Download Resilience**
- **Failed Chunk Retry**: Retry failed chunks
- **Chunk Verification**: Verify downloaded chunks
- **Parallel Chunk Recovery**: Recover failed chunks in parallel

---

## Failure Safety

### Failure Scenarios & Handling

**1. Network Interruption**

**Scenario**: Network connection lost during download.

**Impact**: Download interrupted, partial file.

**Mitigation**:
- **State Persistence**: Save state periodically
- **Resume Support**: Resume from last saved state
- **Retry Logic**: Retry with exponential backoff
- **Connection Monitoring**: Monitor connection health

**Recovery**:
- **Automatic Resume**: Resume when connection restored
- **State Restoration**: Restore from saved state
- **Partial File Handling**: Handle partial files

**2. Server Unavailability**

**Scenario**: Download server becomes unavailable.

**Impact**: Cannot download file.

**Mitigation**:
- **Retry Logic**: Retry with exponential backoff
- **Multiple Mirrors**: Support multiple download sources
- **Timeout Handling**: Handle timeouts gracefully
- **Error Reporting**: Report errors to user

**Recovery**:
- **Retry**: Retry when server available
- **Mirror Fallback**: Fallback to mirror if available
- **Manual Retry**: Allow manual retry

**3. Disk Space Exhaustion**

**Scenario**: Insufficient disk space.

**Impact**: Cannot save downloaded file.

**Mitigation**:
- **Pre-check**: Check disk space before download
- **Error Handling**: Handle disk space errors
- **User Notification**: Notify user of insufficient space

**Recovery**:
- **User Action**: User frees disk space
- **Resume**: Resume download after space available

---

## Scalability Considerations

### 1. Concurrent Downloads

**Multiple Downloads:**
- **Download Queue**: Queue multiple downloads
- **Concurrent Limits**: Limit concurrent downloads
- **Priority Queue**: Prioritize downloads
- **Resource Management**: Manage system resources

**2. Large File Handling**

**Memory Efficiency:**
- **Streaming**: Stream downloads instead of loading in memory
- **Chunk Processing**: Process chunks instead of entire file
- **Memory Limits**: Limit memory usage per download

**3. Bandwidth Management**

**Throttling:**
- **Rate Limiting**: Limit download speed
- **Priority-Based**: Prioritize downloads
- **Adaptive**: Adjust based on network conditions

---

## API Design

### Basic Usage

```python
from filedownloader import FileDownloader

# Simple download
downloader = FileDownloader()
downloader.download(
    url="https://example.com/file.zip",
    destination="/path/to/save/file.zip",
    on_progress=lambda progress: print(f"Progress: {progress}%")
)

# Advanced usage
downloader = FileDownloader(
    chunk_size=1024 * 1024,  # 1MB chunks
    max_parallel_chunks=4,
    retry_count=3,
    timeout=30
)

task = downloader.download(
    url="https://example.com/large-file.zip",
    destination="/path/to/save/large-file.zip",
    on_progress=progress_callback,
    on_complete=complete_callback,
    on_error=error_callback
)

# Pause/Resume
task.pause()
task.resume()
task.cancel()
```

### Queue Management

```python
from filedownloader import DownloadQueue

queue = DownloadQueue(max_concurrent=3)

queue.add(
    url="https://example.com/file1.zip",
    destination="/path/to/file1.zip"
)
queue.add(
    url="https://example.com/file2.zip",
    destination="/path/to/file2.zip"
)

queue.start()
queue.pause_all()
queue.resume_all()
```

---

## Download Strategies

### Strategy 1: Sequential Download

```python
class SequentialDownloadStrategy:
    def download(self, url: str, destination: str, chunk_size: int = 8192):
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(destination, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                downloaded += len(chunk)
                self.on_progress(downloaded, total_size)
```

### Strategy 2: Parallel Chunk Download

```python
class ParallelChunkDownloadStrategy:
    def download(self, url: str, destination: str, num_chunks: int = 4):
        # Get file size
        head_response = requests.head(url)
        total_size = int(head_response.headers.get('content-length', 0))
        chunk_size = total_size // num_chunks
        
        # Download chunks in parallel
        with ThreadPoolExecutor(max_workers=num_chunks) as executor:
            futures = []
            for i in range(num_chunks):
                start = i * chunk_size
                end = start + chunk_size - 1 if i < num_chunks - 1 else total_size - 1
                future = executor.submit(self.download_chunk, url, destination, start, end, i)
                futures.append(future)
            
            # Wait for all chunks
            for future in as_completed(futures):
                future.result()
        
        # Merge chunks
        self.merge_chunks(destination, num_chunks)
    
    def download_chunk(self, url: str, destination: str, start: int, end: int, chunk_id: int):
        headers = {'Range': f'bytes={start}-{end}'}
        response = requests.get(url, headers=headers, stream=True)
        
        chunk_file = f"{destination}.chunk{chunk_id}"
        with open(chunk_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    
    def merge_chunks(self, destination: str, num_chunks: int):
        with open(destination, 'wb') as outfile:
            for i in range(num_chunks):
                chunk_file = f"{destination}.chunk{i}"
                with open(chunk_file, 'rb') as infile:
                    outfile.write(infile.read())
                os.remove(chunk_file)
```

---

## Resume & Retry Logic

### Resume Implementation

```python
class ResumableDownload:
    def __init__(self, url: str, destination: str):
        self.url = url
        self.destination = destination
        self.metadata_file = f"{destination}.meta"
    
    def download(self):
        # Load metadata if exists
        if os.path.exists(self.metadata_file):
            metadata = self.load_metadata()
            start_byte = metadata['downloaded_bytes']
        else:
            start_byte = 0
        
        # Check if server supports range requests
        headers = {}
        if start_byte > 0:
            headers['Range'] = f'bytes={start_byte}-'
        
        response = requests.get(self.url, headers=headers, stream=True)
        
        # Append mode if resuming
        mode = 'ab' if start_byte > 0 else 'wb'
        
        with open(self.destination, mode) as f:
            downloaded = start_byte
            total_size = int(response.headers.get('content-length', 0)) + start_byte
            
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                self.save_metadata(downloaded, total_size)
                self.on_progress(downloaded, total_size)
    
    def save_metadata(self, downloaded: int, total: int):
        metadata = {
            'downloaded_bytes': downloaded,
            'total_bytes': total,
            'url': self.url,
            'timestamp': time.time()
        }
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f)
    
    def load_metadata(self) -> dict:
        with open(self.metadata_file, 'r') as f:
            return json.load(f)
```

### Retry Logic

```python
class RetryManager:
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def execute_with_retry(self, func, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except (requests.RequestException, IOError) as e:
                if attempt == self.max_retries - 1:
                    raise
                
                wait_time = self.backoff_factor ** attempt
                time.sleep(wait_time)
                continue
```

---

## Progress Tracking

```python
class ProgressTracker:
    def __init__(self, total_size: int):
        self.total_size = total_size
        self.downloaded = 0
        self.start_time = time.time()
        self.last_update_time = time.time()
        self.last_downloaded = 0
    
    def update(self, bytes_downloaded: int):
        self.downloaded = bytes_downloaded
        
        current_time = time.time()
        elapsed = current_time - self.start_time
        time_since_last_update = current_time - self.last_update_time
        
        # Calculate speed
        bytes_since_last_update = self.downloaded - self.last_downloaded
        if time_since_last_update > 0:
            speed = bytes_since_last_update / time_since_last_update
        else:
            speed = 0
        
        # Calculate ETA
        remaining_bytes = self.total_size - self.downloaded
        if speed > 0:
            eta_seconds = remaining_bytes / speed
        else:
            eta_seconds = 0
        
        # Calculate percentage
        percentage = (self.downloaded / self.total_size) * 100 if self.total_size > 0 else 0
        
        self.last_update_time = current_time
        self.last_downloaded = self.downloaded
        
        return {
            'downloaded': self.downloaded,
            'total': self.total_size,
            'percentage': percentage,
            'speed': speed,
            'eta_seconds': eta_seconds,
            'elapsed_seconds': elapsed
        }
```

---

## Error Handling

```python
class DownloadError(Exception):
    pass

class NetworkError(DownloadError):
    pass

class InvalidURLError(DownloadError):
    pass

class InsufficientSpaceError(DownloadError):
    pass

class FileDownloader:
    def download(self, url: str, destination: str):
        try:
            # Validate URL
            if not self.is_valid_url(url):
                raise InvalidURLError(f"Invalid URL: {url}")
            
            # Check disk space
            if not self.has_sufficient_space(destination, url):
                raise InsufficientSpaceError("Insufficient disk space")
            
            # Perform download
            self._download(url, destination)
            
        except requests.RequestException as e:
            raise NetworkError(f"Network error: {e}")
        except IOError as e:
            raise DownloadError(f"IO error: {e}")
```

---

## Performance Optimization

1. **Chunk Size Tuning**: Optimal chunk size (1MB-4MB)
2. **Connection Pooling**: Reuse HTTP connections
3. **Compression**: Support gzip/deflate
4. **Concurrent Downloads**: Multiple files in parallel
5. **Memory Management**: Stream instead of loading entire file

---

## Security Considerations

- **URL Validation**: Validate URLs before downloading
- **File Type Validation**: Check file extensions/types
- **Size Limits**: Enforce maximum file size
- **Path Traversal Protection**: Sanitize destination paths
- **HTTPS Only**: Option to enforce HTTPS

---

## Testing Strategy

```python
# Unit tests
def test_sequential_download():
    strategy = SequentialDownloadStrategy()
    strategy.download("http://test.com/file.txt", "/tmp/file.txt")
    assert os.path.exists("/tmp/file.txt")

# Integration tests
def test_resume_download():
    downloader = ResumableDownload("http://test.com/file.txt", "/tmp/file.txt")
    # Simulate interruption
    downloader.download()  # Partial download
    # Resume
    downloader.download()  # Should resume from where it left off
```

---

## Interview Discussion Points

1. **Resume Logic**: How do you implement resumable downloads?
2. **Parallel Downloads**: How do you download chunks in parallel?
3. **Progress Tracking**: How do you calculate download speed and ETA?
4. **Error Handling**: How do you handle network failures?

---

**Document Version**: 1.0  
**Last Updated**: January 2024

