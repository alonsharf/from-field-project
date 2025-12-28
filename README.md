# From Field to You

A clean and simple agricultural supply chain management system with **API-first architecture**. Features a FastAPI backend microservices pattern and a Streamlit frontend that communicates entirely through HTTP API calls.

## Project Overview

This is an agricultural supply chain management system called "From Field to You" with a **super clean, single-farmer architecture**:
- **API Layer**: FastAPI with dedicated microservices (auth, farmer, products, orders, etc.)
- **Frontend Layer**: Streamlit with direct API integration (no database dependencies)
- **Data Layer**: PostgreSQL with proper relationships and sample data
- **Authentication**: Centralized auth microservice with bcrypt password hashing
- **Single Farmer Model**: Simplified for single farm operations

The system provides core farm-to-customer functionality with clean workflows. **The frontend calls the API directly via HTTP requests** - no intermediate layers or direct database connections.

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed

### Running the Application

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd from_field_to_you
   ```

2. **Start all services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - **Streamlit Frontend**: http://localhost:8501 (Full farm management system)
   - **FastAPI Backend**: http://localhost:8000 (API documentation)
   - **PostgreSQL Database**: localhost:5432 (Direct database access)
   - **pgAdmin**: http://localhost:8080 (Database management - admin@admin.com / admin)

4. **Connect to database via pgAdmin**
   - Open pgAdmin: http://localhost:8080
   - Login with: `admin@admin.com` / `admin`
   - Add new server connection:
     - **Host**: `postgres` (Docker service name)
     - **Port**: `5432`
     - **Database**: `from_field_to_you`
     - **Username**: `farm_user`
     - **Password**: `farm_password`

5. **Test login credentials**

   **Admin/Farmer Login:**
   - Email: `john@greenvalley.com`
   - Password: `admin123`

   **Customer Login:**
   - Email: `alice@example.com`
   - Password: `password123`

### Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart frontend

# Stop all services
docker-compose down

# Rebuild and start (after code changes)
docker-compose build --no-cache
docker-compose up -d

# Access database directly
docker exec -it from_field_to_you_db psql -U farm_user -d from_field_to_you
```

## Manual Setup (Alternative)

### Prerequisites
- Python 3.8+
- PostgreSQL

### Installation

1. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup PostgreSQL database**
   ```bash
   createdb from_field_to_you
   psql from_field_to_you < packages/db/schema/tables.sql
   psql from_field_to_you < packages/db/schema/inserts.sql
   ```

4. **Configure environment**
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost:5432/from_field_to_you"
   ```

5. **Run the application**
   ```bash
   # Start FastAPI backend (REQUIRED - frontend depends on it)
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

   # Start Streamlit frontend (in another terminal)
   streamlit run streamlit_app/main.py --server.port 8502
   ```

## Architecture

### Complete 3-Layer Architecture
- **API Layer**: FastAPI routes with Pydantic validation
- **Service Layer**: Business logic and database operations
- **Data Layer**: SQLAlchemy ORM models with PostgreSQL

### Key Features
- ✅ **Authentication System** with bcrypt password hashing
- ✅ **Single Farmer Admin** system for streamlined management
- ✅ **Complete CRUD Operations** for all entities
- ✅ **SQLAlchemy ORM Integration** with async support
- ✅ **Pydantic Models** for request/response validation
- ✅ **Service Layer Pattern** for clean architecture
- ✅ **Database Schema** with proper relationships
- ✅ **Business Logic** (stock management, order workflow)
- ✅ **Professional API Documentation** with Swagger
- ✅ **Streamlit Integration** with persona-driven portals

## Project Structure

```
from_field_to_you/
├── api/                         # FastAPI Backend
│   ├── main.py                  # FastAPI app with router configurations
│   ├── auth/                    # Authentication microservice
│   │   ├── routes.py            # Login, register, admin farmer endpoints
│   │   ├── service.py           # Auth business logic
│   │   └── models.py            # Auth request/response models
│   ├── farmer/                  # Single farmer management
│   ├── customers/               # Customer management service
│   ├── products/                # Product catalog service
│   ├── orders/                  # Order processing service
│   ├── shipments/               # Shipment tracking service
│   ├── cart/                    # Shopping cart service
│   └── analytics/               # Analytics and reporting service
├── streamlit_app/               # Frontend - Direct API Integration
│   ├── main.py                  # Streamlit app with HTTP API calls
│   └── pages/                   # Portal pages
│       ├── farmer/              # Farmer Portal
│       └── customer/            # Customer Portal
├── packages/                    # Essential Infrastructure
│   └── db/                      # Database components
│       ├── models.py            # SQLAlchemy ORM models
│       ├── session.py           # Database session management
│       └── schema/              # Database Schema
│           ├── tables.sql       # PostgreSQL DDL with all tables
│           └── inserts.sql      # Sample data with authentication
├── requirements.txt             # Project dependencies
└── README.md                    # Documentation
```


## Authentication System

### 🔐 Security Features
- **Password hashing** using bcrypt for security
- **Session management** with proper logout functionality
- **Email uniqueness** constraints to prevent duplicate accounts
- **Role-based access** (Farmer Admin vs Customer)

### 👨‍🌾 Admin (Farmer) Portal
- **Single farmer admin** - only one farmer manages the entire system
- **Full inventory management** - add, edit, view all products
- **Order fulfillment** - manage all customer orders
- **Customer management** - view and manage all customers
- **Shipment tracking** - handle logistics for all orders

### 🛒 Customer Portal
- **Customer registration** for new users
- **Product browsing** - view all products from the single farm
- **Shopping cart** - add items and checkout
- **Order tracking** - view order history and shipment status
- **Profile management** - update personal information and addresses

## Database Schema

The system uses PostgreSQL with the following main entities:

### Core Tables
- **farmer** - Farmer profiles with authentication
- **customer** - Customer accounts with authentication
- **product** - Product catalog with inventory management
- **orders** - Order processing with status tracking
- **purchase** - Order line items linking products to orders
- **shipment** - Shipment tracking and delivery management
- **cart** - Shopping cart management
- **cart_item** - Items in shopping carts
- **customer_session** - User session management
- **farmer_profile** - Extended farmer information and branding

### Key Features
- **UUID Primary Keys** for all entities using PostgreSQL's `gen_random_uuid()`
- **Enum Types** for status fields (OrderStatus, PaymentStatus, ShipmentStatus)
- **Proper Foreign Keys** with SQLAlchemy relationships
- **Automatic Timestamps** with `server_default=func.now()`
- **Business Constraints** enforced at database level
- **Authentication Fields** (password_hash) with bcrypt encryption

## API Endpoints

### Core Endpoints
- `GET /` - API welcome and information
- `GET /health` - Health check status

### 🔐 Authentication Service (`/api/auth/`)
- `POST /farmer/login` - Farmer login with email/password
- `POST /customer/login` - Customer login with email/password
- `POST /customer/register` - Register new customer account
- `GET /farmer/admin` - Get admin farmer info (single farmer model)

### 👨‍🌾 Farmer Service (`/api/farmer/`) - Single Farmer Model
- `GET /admin` - Get the admin farmer (single farmer operations)
- `PUT /admin` - Update admin farmer profile
- `GET /profile` - Get extended farmer profile information

### 👥 Customers Service (`/api/customers/`)
- `GET /` - List customers with pagination
- `GET /{customer_id}` - Get customer by ID
- `POST /` - Create new customer with email validation
- `PUT /{customer_id}` - Update customer
- `DELETE /{customer_id}` - Delete customer
- `GET /search/` - Search customers
- `GET /{customer_id}/orders` - Get customer with order history

### 🥕 Products Service (`/api/products/`)
- `GET /` - List products with advanced filtering
- `GET /{product_id}` - Get product by ID
- `POST /` - Create new product
- `PUT /{product_id}` - Update product
- `DELETE /{product_id}` - Delete product
- `GET /search/` - Search products
- `GET /category/{category}` - Get products by category
- `GET /farmer/{farmer_id}` - Get products by farmer
- `PUT /{product_id}/stock` - Update product stock
- `GET /low-stock/` - Get low stock products

### 📦 Orders Service (`/api/orders/`)
- `GET /` - List orders with filtering
- `GET /{order_id}` - Get order with full details
- `POST /` - Create order with automatic stock updates
- `PUT /{order_id}` - Update order
- `DELETE /{order_id}` - Delete order (DRAFT only)
- `PUT /{order_id}/status` - Update order status
- `PUT /{order_id}/payment` - Update payment status
- `PUT /{order_id}/cancel` - Cancel order and restore stock
- `GET /customer/{customer_id}` - Get customer orders
- `GET /farmer/{farmer_id}` - Get farmer orders

### 🚚 Shipments Service (`/api/shipments/`)
- `GET /` - List shipments with filtering
- `GET /{shipment_id}` - Get shipment by ID
- `POST /` - Create new shipment
- `PUT /{shipment_id}` - Update shipment
- `DELETE /{shipment_id}` - Delete shipment
- `PUT /{shipment_id}/status` - Update shipment status
- `PUT /{shipment_id}/deliver` - Mark as delivered
- `PUT /{shipment_id}/cancel` - Cancel shipment
- `POST /ship-order` - Ship an order
- `GET /order/{order_id}` - Get shipment by order
- `GET /tracking/{tracking_number}` - Track by number
- `GET /search/` - Search shipments
- `GET /status/{status}` - Get shipments by status

## Business Features

### 🔄 Complete Order Workflow
1. **Create Order** - Customer places order with multiple products
2. **Stock Validation** - Automatic inventory checks and updates
3. **Payment Processing** - Status tracking and reference management
4. **Order Fulfillment** - Status progression from DRAFT → PAID → FULFILLED
5. **Shipment Creation** - Automatic shipment generation with tracking
6. **Delivery Tracking** - Real-time status updates and customer notifications

### 📊 Inventory Management
- **Real-time Stock Updates** - Automatic adjustments on order creation/cancellation
- **Low Stock Alerts** - Configurable threshold monitoring
- **Stock Movement Tracking** - Complete audit trail of inventory changes
- **Product Availability** - Date-based availability windows

### 🔍 Advanced Search & Filtering
- **Multi-field Search** - Name, description, category across all entities
- **Dynamic Filtering** - Status, dates, categories, relationships
- **Pagination Support** - Efficient large dataset handling
- **Relationship Navigation** - Easy access to related data

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/from_field_to_you
DATABASE_ECHO=false

# API Configuration
API_TITLE=From Field to You API
API_VERSION=1.0.0
API_DESCRIPTION=Agricultural supply chain management API

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services (add as needed)
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-email-password
```

## Troubleshooting

### Authentication Issues
```bash
# "bcrypt not found" Error
pip install bcrypt==4.1.2
# or rebuild Docker
docker-compose build --no-cache
```

### Database Connection Issues
```bash
# Check all services are running
docker-compose ps

# Check database logs
docker-compose logs postgres

# Restart services
docker-compose restart
```

### "No admin farmer found" Error
Verify that there's an active farmer in the database:
```sql
SELECT id, name, email, is_active FROM farmer WHERE is_active = true;
```

## Security Notes

- **Default passwords** are provided for testing - change them in production
- **Password hashing** uses bcrypt with appropriate salt rounds
- **Session management** clears sensitive data on logout
- **Email uniqueness** prevents duplicate accounts

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Architecture Benefits

### Core Principles
- **API-First**: Frontend communicates entirely through HTTP requests
- **Centralized Auth**: Dedicated authentication microservice handles all auth operations
- **Single Farmer**: Simplified for single farm operations
- **Direct Integration**: HTTP calls from Streamlit to FastAPI
- **Minimal Dependencies**: Only essential packages

### Benefits
1. **Easy to Maintain** - Clear separation between frontend and backend
2. **Scalable** - API can be used by mobile apps, other frontends, or external integrations
3. **Secure** - All business logic and validation in the API layer
4. **Fast Development** - Direct API calls without complex abstractions
5. **Future-Ready** - API-first approach enables mobile apps and integrations

## Deploy to AWS (ECS + RDS)

This project includes Terraform to deploy a production-ready 3-tier setup:
- API and Frontend run as isolated ECS Fargate services behind separate ALBs
- PostgreSQL database runs in Amazon RDS (private subnets)
- DATABASE_URL is provided via AWS Secrets Manager; SSL is enforced

### Prerequisites
- AWS account and credentials configured (`aws configure`)
- Terraform >= 1.5
- Docker (to build images)

### 1) Build and tag images
Use the single `Dockerfile` for both services. Tag separately:
```bash
# From repo root
docker build -t api:latest .
docker build -t frontend:latest .
```

### 2) Initialize Terraform
```bash
cd infra/terraform
terraform init
```

### 3) Plan/apply core infrastructure
Optionally create a `terraform.tfvars` file:
```hcl
project     = "from-field"
environment = "dev"
aws_region  = "us-east-1"
db_name     = "from_field_to_you"
db_username = "app_user"
```
Apply:
```bash
terraform apply
```
Note the outputs:
- `ecr_api_repository_url`
- `ecr_frontend_repository_url`
- `api_load_balancer_dns`
- `frontend_load_balancer_dns`

### 4) Push images to ECR
```bash
# Authenticate to ECR
aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com

# Tag and push using Terraform outputs (replace below with actual values)
docker tag api:latest <ECR_API_REPO_URL>:latest
docker push <ECR_API_REPO_URL>:latest

docker tag frontend:latest <ECR_FRONTEND_REPO_URL>:latest
docker push <ECR_FRONTEND_REPO_URL>:latest
```

### 5) Point ECS tasks to the pushed images
Update the Terraform variables (or use `-var`) to set:
```hcl
api_image      = "<ECR_API_REPO_URL>:latest"
frontend_image = "<ECR_FRONTEND_REPO_URL>:latest"
```
Then:
```bash
terraform apply
```

### 6) Access services
- API base URL: `http://<api_load_balancer_dns>`
- Frontend URL: `http://<frontend_load_balancer_dns>`

The frontend receives `API_BASE_URL` at runtime and calls the API ALB directly.

### Database connection and SSL
- The backend reads `DATABASE_URL` from the environment (Secrets Manager → ECS task env)
- SSL is enforced by setting `sslmode=require` in the secret
- Optional: set `DATABASE_SSLMODE=require` to ensure async driver uses SSL

### Notes
- Both services use the same image build, with different ECS container commands
- The RDS instance is private and only accessible from ECS service security groups
- Consider adding Route53 DNS, HTTPS (ACM + ALB listeners), autoscaling, and WAF for production