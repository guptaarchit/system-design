# Develop a Photo Sharing Platform like Flickr or Google Photos

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Photo Upload Flow](#photo-upload-flow)
7. [Photo Processing Pipeline](#photo-processing-pipeline)
8. [Photo Storage Strategy](#photo-storage-strategy)
9. [Scalability Considerations](#scalability-considerations)
10. [Caching Strategy](#caching-strategy)
11. [Security](#security)
12. [Capacity Planning](#capacity-planning)
13. [Technology Stack](#technology-stack)
14. [Failure Scenarios & Handling](#failure-scenarios--handling)
15. [Trade-offs & Design Decisions](#trade-offs--design-decisions)
16. [Interview Discussion Points](#interview-discussion-points)

---

## Overview

A photo sharing platform that allows users to upload, store, organize, and share photos. The system must handle millions of photos, support various image formats, provide photo processing (thumbnails, resizing), enable sharing and collaboration, and scale to millions of users.

**Key Features:**
- Photo upload and storage
- Photo organization (albums, tags)
- Photo sharing and permissions
- Photo processing (thumbnails, resizing)
- Search and discovery
- Photo metadata management
- Mobile and web clients
- Offline sync

---

## Requirements

### Functional Requirements

1. **Photo Management**
   - Upload photos (various formats)
   - Organize into albums
   - Tag photos
   - Delete photos
   - Photo versioning

2. **Photo Processing**
   - Generate thumbnails
   - Resize images
   - Extract metadata (EXIF)
   - Face detection
   - Auto-tagging

3. **Sharing**
   - Share with specific users
   - Public/private albums
   - Share links
   - Permission levels

4. **Search**
   - Search by tags
   - Search by location
   - Search by date
   - Face recognition search

### Non-Functional Requirements

1. **Scalability**
   - Support 1B+ photos
   - Handle 10M+ uploads per day
   - Support 100M+ users
   - Horizontal scaling

2. **Performance**
   - Upload: < 5 seconds for 10MB photo
   - Thumbnail generation: < 2 seconds
   - Photo load: < 500ms
   - Search: < 300ms

3. **Storage**
   - Efficient storage (compression)
   - Multiple storage tiers
   - Backup and replication

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Web App, Mobile Apps)                                         │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer                   │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────┐      ┌────────────────────────────┐
│   Photo Service            │      │   Metadata Service        │
│   - Upload/Download        │      │   - Albums, Tags           │
└────────────┬───────────────┘      └────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                    Message Queue                                 │
│              (Kafka)                                            │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Processing Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Thumbnail  │  │   Resize     │  │   Metadata   │         │
│  │   Generator  │  │   Service    │  │   Extractor  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Storage Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Original   │  │   Thumbnails │  │   Metadata   │         │
│  │   Photos     │  │              │  │              │         │
│  │  (S3/HDFS)   │  │  (S3/HDFS)   │  │ (PostgreSQL) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

---

## Database Design

### Photos Table

```sql
CREATE TABLE photos (
    photo_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    album_id BIGINT,
    original_filename VARCHAR(255),
    storage_path VARCHAR(500) NOT NULL,
    thumbnail_path VARCHAR(500),
    file_size BIGINT,
    width INTEGER,
    height INTEGER,
    mime_type VARCHAR(50),
    exif_data JSONB,
    tags TEXT[],
    location JSONB, -- {lat, lng, address}
    taken_at TIMESTAMP,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    is_public BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (album_id) REFERENCES albums(album_id),
    INDEX idx_user_id (user_id),
    INDEX idx_album_id (album_id),
    INDEX idx_tags (tags),
    INDEX idx_taken_at (taken_at)
);
```

### Albums Table

```sql
CREATE TABLE albums (
    album_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cover_photo_id BIGINT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user_id (user_id)
);
```

### Photo Shares Table

```sql
CREATE TABLE photo_shares (
    share_id BIGSERIAL PRIMARY KEY,
    photo_id BIGINT NOT NULL,
    shared_by BIGINT NOT NULL,
    shared_with_user_id BIGINT,
    shared_with_email VARCHAR(255),
    permission VARCHAR(20) DEFAULT 'view', -- view, edit
    share_token VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (photo_id) REFERENCES photos(photo_id)
);
```

---

## API Design

### Photo APIs

```
POST   /api/v1/photos/upload
GET    /api/v1/photos/{photo_id}
DELETE /api/v1/photos/{photo_id}
GET    /api/v1/photos?album_id={album_id}&page=1&limit=50
POST   /api/v1/photos/{photo_id}/share
GET    /api/v1/photos/search?q={query}&tags={tags}
```

### Upload Request

```json
POST /api/v1/photos/upload
Content-Type: multipart/form-data

{
  "file": <binary>,
  "album_id": 123,
  "tags": ["vacation", "beach"],
  "is_public": false
}
```

---

## Photo Upload Flow

### Upload Process

1. **Client uploads photo**
2. **Service validates file** (size, type)
3. **Service stores original** in object storage
4. **Service creates photo record** in database
5. **Service queues processing** (thumbnails, metadata)
6. **Processors generate thumbnails**
7. **Processors extract metadata**
8. **Service updates photo record**

### Chunked Upload

```python
class PhotoUploader:
    def upload_photo(self, file, chunk_size=5*1024*1024):  # 5MB chunks
        # Initiate multipart upload
        upload_id = self.initiate_upload(file.name, file.size)
        
        chunks = []
        part_number = 1
        
        # Upload chunks
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            
            etag = self.upload_chunk(upload_id, part_number, chunk)
            chunks.append({'part_number': part_number, 'etag': etag})
            part_number += 1
        
        # Complete upload
        return self.complete_upload(upload_id, chunks)
```

---

## Photo Processing Pipeline

### Processing Flow

```python
class PhotoProcessor:
    def process_photo(self, photo_id: int):
        # Get photo
        photo = self.get_photo(photo_id)
        
        # Generate thumbnails
        thumbnails = self.generate_thumbnails(photo)
        
        # Extract metadata
        metadata = self.extract_metadata(photo)
        
        # Face detection
        faces = self.detect_faces(photo)
        
        # Auto-tagging
        tags = self.auto_tag(photo)
        
        # Update photo record
        self.update_photo(photo_id, {
            'thumbnails': thumbnails,
            'metadata': metadata,
            'faces': faces,
            'tags': tags
        })
```

### Thumbnail Generation

```python
from PIL import Image

def generate_thumbnails(photo_path: str, sizes: list = [(150, 150), (300, 300), (800, 800)]):
    thumbnails = {}
    img = Image.open(photo_path)
    
    for size in sizes:
        thumbnail = img.copy()
        thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
        thumbnail_path = f"{photo_path}_thumb_{size[0]}x{size[1]}.jpg"
        thumbnail.save(thumbnail_path, "JPEG", quality=85)
        thumbnails[f"{size[0]}x{size[1]}"] = thumbnail_path
    
    return thumbnails
```

---

## Photo Storage Strategy

### Storage Tiers

1. **Hot Storage**: Recent photos (last 30 days) - Fast access
2. **Warm Storage**: Older photos (30-365 days) - Standard access
3. **Cold Storage**: Archived photos (365+ days) - Archive

### Storage Optimization

- **Compression**: JPEG quality optimization
- **Deduplication**: Store identical photos once
- **CDN**: Cache frequently accessed photos
- **Multiple Formats**: Store original + processed versions

---

## Scalability Considerations

- **Horizontal Scaling**: Multiple upload and processing servers
- **Storage Sharding**: Shard by user_id or photo_id
- **CDN**: Distribute photo delivery
- **Async Processing**: Process thumbnails asynchronously

---

## Capacity Planning

- **Users**: 100M users
- **Photos per User**: 1,000 average
- **Total Photos**: 100B photos
- **Average Photo Size**: 3MB
- **Total Storage**: 100B × 3MB = 300PB
- **Daily Uploads**: 10M photos/day = 30TB/day

---

## Technology Stack

- **Backend**: Go, Java, Python
- **Storage**: S3, HDFS
- **Database**: PostgreSQL, Cassandra
- **Processing**: ImageMagick, PIL, OpenCV
- **CDN**: CloudFlare, AWS CloudFront

---

## High-Level Design (HLD)

### System Overview

The photo sharing platform follows a microservices architecture:

1. **Client Layer**: Web and mobile applications
2. **API Gateway**: Routes requests, handles authentication
3. **Photo Service**: Photo upload, download, management
4. **Processing Layer**: Image processing workers (thumbnails, resizing)
5. **Storage Layer**: Object storage (S3) for photos, CDN for delivery
6. **Metadata Service**: Albums, tags, sharing management

### Component Architecture

**Core Services:**
- **Photo Service**: Photo CRUD operations
- **Processing Service**: Image processing coordination
- **Metadata Service**: Albums, tags, sharing
- **Search Service**: Photo search and discovery

---

## Low-Level Design (LLD)

### Photo Upload Service

```python
class PhotoUploadService:
    def __init__(self, s3_client, kafka_producer, db_client):
        self.s3 = s3_client
        self.kafka = kafka_producer
        self.db = db_client
    
    def upload_photo(self, file, user_id: int, album_id: int = None) -> dict:
        # Validate file
        if not self.validate_file(file):
            raise ValueError("Invalid file")
        
        # Generate photo ID
        photo_id = uuid.uuid4()
        
        # Upload to S3 (chunked for large files)
        s3_key = f"photos/{user_id}/{photo_id}/original"
        upload_url = self.s3.upload_chunked(s3_key, file)
        
        # Create photo record
        photo = {
            'photo_id': photo_id,
            'user_id': user_id,
            'album_id': album_id,
            'storage_path': s3_key,
            'file_size': file.size,
            'mime_type': file.content_type,
            'status': 'uploading',
            'created_at': datetime.utcnow()
        }
        
        photo_id = self.db.execute(
            """
            INSERT INTO photos (photo_id, user_id, album_id, storage_path, file_size, mime_type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            RETURNING photo_id
            """,
            [photo_id, user_id, album_id, s3_key, file.size, file.content_type, 'uploading']
        )
        
        # Queue for processing
        self.kafka.send('photo-processing', {
            'photo_id': photo_id,
            'storage_path': s3_key,
            'user_id': user_id
        })
        
        return {'photo_id': photo_id, 'status': 'uploading'}
```

### Image Processing Worker

```python
class ImageProcessingWorker:
    def __init__(self, s3_client, db_client):
        self.s3 = s3_client
        self.db = db_client
    
    def process_photo(self, photo_id: int, storage_path: str):
        # Download original
        original = self.s3.download(storage_path)
        
        # Generate thumbnails
        sizes = {
            'thumbnail': (150, 150),
            'small': (320, 320),
            'medium': (640, 640),
            'large': (1080, 1080)
        }
        
        processed_urls = {}
        for size_name, (width, height) in sizes.items():
            # Resize
            resized = self.resize_image(original, width, height)
            
            # Compress
            compressed = self.compress_image(resized)
            
            # Upload
            s3_key = f"{storage_path.rsplit('/', 1)[0]}/{size_name}.jpg"
            url = self.s3.upload(s3_key, compressed)
            processed_urls[size_name] = url
        
        # Extract metadata
        metadata = self.extract_metadata(original)
        
        # Update photo record
        self.db.execute(
            """
            UPDATE photos 
            SET thumbnail_path = ?, width = ?, height = ?, exif_data = ?, status = 'processed'
            WHERE photo_id = ?
            """,
            [processed_urls['thumbnail'], metadata['width'], metadata['height'], 
             json.dumps(metadata['exif']), photo_id]
        )
```

---

## Fault Tolerance

### Processing Resilience

**Worker Failure:**
- Multiple worker instances
- Retry failed processing jobs
- Dead letter queue for persistent failures

**Storage Resilience:**
- S3 with replication
- Multiple storage regions
- Backup strategy

---

## Optimizations

### Storage Optimization

**Compression:**
- JPEG quality optimization
- WebP for better compression
- Lazy loading of high-res images

**CDN Optimization:**
- Cache photos at edge
- Pre-position popular photos
- Regional distribution

### Processing Optimization

**Parallel Processing:**
- Process multiple sizes in parallel
- Use worker pools
- Optimize image processing

---

## Failure Safety

### Upload Failure

**Scenario: Upload Interrupted**
- **Impact**: Photo not uploaded
- **Mitigation**:
  - Resume upload capability
  - Chunked uploads
  - Retry logic
- **Recovery**:
  - Resume from last chunk
  - Complete upload
  - Process photo

### Processing Failure

**Scenario: Processing Worker Fails**
- **Impact**: Photo not processed
- **Mitigation**:
  - Retry processing
  - Dead letter queue
  - Manual reprocessing
- **Recovery**:
  - Worker recovers
  - Process failed jobs
  - Verify processing

---

## Scalability

### Horizontal Scaling

**Service Scaling:**
- Stateless service instances
- Load balancer distributes requests
- Scale independently

**Worker Scaling:**
- Add more worker instances
- Scale based on queue depth
- Process in parallel

### Storage Scaling

**Object Storage:**
- S3 scales automatically
- Distribute across regions
- Use CDN for delivery

---

## Interview Discussion Points

1. **Upload**: How do you handle large file uploads?
2. **Processing**: How do you process millions of photos?
3. **Storage**: How do you store petabytes of photos?
4. **Search**: How do you search billions of photos?

---

**Document Version**: 1.0  
**Last Updated**: January 2024

