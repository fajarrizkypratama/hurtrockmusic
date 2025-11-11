# 🎸 FLOWCHARTS-DIAGRAM.md - Hurtrock Music Store

Dokumentasi lengkap flowchart dan diagram untuk sistem e-commerce alat musik Hurtrock Music Store dengan arsitektur Flask-only dan chat service Django.

## 📊 Daftar Isi

1. [Arsitektur Sistem](#arsitektur-sistem)
2. [Entity Relationship Diagram (ERD)](#entity-relationship-diagram-erd)
3. [Data Flow Diagram (DFD)](#data-flow-diagram-dfd)
4. [Use Case Diagram](#use-case-diagram)
5. [Customer Journey Flowchart](#customer-journey-flowchart)
6. [Admin Workflow Flowchart](#admin-workflow-flowchart)
7. [Order Processing Flowchart](#order-processing-flowchart)
8. [Payment Processing Flowchart](#payment-processing-flowchart)
9. [Authentication Flow](#authentication-flow)
10. [Cart Management Flow](#cart-management-flow)
11. [Product Management Flow](#product-management-flow)
12. [Inventory Management Flow](#inventory-management-flow)
13. [Chat System Flow](#chat-system-flow)
14. [Error Handling Flow](#error-handling-flow)
15. [Deployment Architecture](#deployment-architecture)

---

## 🏗️ Arsitektur Sistem

### Flask-Only Architecture dengan Chat Service

```mermaid
graph TD
    subgraph "Cloud Production Environment"
        MainApp[main.py<br/>Flask Application<br/>Port 5000]
        ChatService[Django Chat Service<br/>Port 8000]

        subgraph "Flask Components"
            WebStore[Web Store Interface]
            AdminPanel[Admin Panel Interface]
            StaticFiles[Static Files Server]
            APIEndpoints[API Endpoints]
        end

        subgraph "Django Components"
            WebSocket[WebSocket Handler]
            ChatAPI[Chat REST API]
            ChatModels[Chat Models]
        end

        Database[(PostgreSQL<br/>Main Database)]
        ChatDB[(SQLite<br/>Chat Database)]
    end

    MainApp --> WebStore
    MainApp --> AdminPanel
    MainApp --> StaticFiles
    MainApp --> APIEndpoints

    ChatService --> WebSocket
    ChatService --> ChatAPI
    ChatService --> ChatModels

    MainApp --> Database
    ChatService --> ChatDB

    MainApp -.->|JWT Token Auth| ChatService
    WebStore -.->|WebSocket| ChatService
    AdminPanel -.->|WebSocket| ChatService
```

### Component Layer Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[User Interface<br/>Jinja2 Templates + Bootstrap]
        JS[Frontend JavaScript<br/>Vanilla JS + WebSocket]
    end

    subgraph "Application Layer"
        Routes[Flask Routes]
        Auth[Authentication<br/>Flask-Login]
        CSRF[CSRF Protection<br/>Flask-WTF]
    end

    subgraph "Business Logic Layer"
        ProductMgmt[Product Management]
        OrderMgmt[Order Management]
        UserMgmt[User Management]
        PaymentMgmt[Payment Processing]
        ChatMgmt[Chat Management]
    end

    subgraph "Data Access Layer"
        ORM[SQLAlchemy ORM]
        Models[Database Models]
    end

    subgraph "External Services"
        Stripe[Stripe Payment Gateway]
        Midtrans[Midtrans Payment Gateway]
        ChatService[Django Chat Service]
    end

    subgraph "Storage Layer"
        PostgresDB[(PostgreSQL Database)]
        FileStorage[Static File Storage]
    end

    UI --> Routes
    JS --> Routes
    Routes --> Auth
    Routes --> CSRF
    Routes --> ProductMgmt
    Routes --> OrderMgmt
    Routes --> UserMgmt
    Routes --> PaymentMgmt
    Routes --> ChatMgmt

    ProductMgmt --> ORM
    OrderMgmt --> ORM
    UserMgmt --> ORM
    PaymentMgmt --> ORM

    PaymentMgmt --> Stripe
    PaymentMgmt --> Midtrans
    ChatMgmt --> ChatService

    ORM --> Models
    Models --> PostgresDB
    Routes --> FileStorage
```

---

## 🗃️ Entity Relationship Diagram (ERD)

### Complete Database Schema

```mermaid
erDiagram
    User {
        int id PK
        string email UK
        string password_hash
        string name
        string phone
        text address
        boolean active
        string role
        datetime created_at
    }

    Category {
        int id PK
        string name
        text description
        string image_url
        boolean is_active
        datetime created_at
    }

    Product {
        int id PK
        string name
        text description
        decimal price
        int stock_quantity
        string image_url
        string brand
        string model
        boolean is_active
        boolean is_featured
        int category_id FK
        int supplier_id FK
        decimal weight
        decimal length
        decimal width
        decimal height
        int minimum_stock
        int low_stock_threshold
        datetime created_at
    }

    ProductImage {
        int id PK
        int product_id FK
        string image_url
        boolean is_thumbnail
        int display_order
        datetime created_at
    }

    CartItem {
        int id PK
        int user_id FK
        int product_id FK
        int quantity
        datetime created_at
    }

    Order {
        int id PK
        int user_id FK
        decimal total_amount
        string status
        string tracking_number
        string courier_service
        int shipping_service_id FK
        decimal shipping_cost
        text shipping_address
        string payment_method
        int estimated_delivery_days
        datetime created_at
        datetime updated_at
    }

    OrderItem {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal price
    }

    Supplier {
        int id PK
        string name
        string contact_person
        string email
        string phone
        text address
        string company
        text notes
        boolean is_active
        datetime created_at
    }

    ShippingService {
        int id PK
        string name
        string code UK
        decimal base_price
        decimal price_per_kg
        decimal price_per_km
        decimal volume_factor
        int min_days
        int max_days
        boolean is_active
        datetime created_at
    }

    PaymentConfiguration {
        int id PK
        string provider
        boolean is_active
        boolean is_sandbox
        string midtrans_client_key
        string midtrans_server_key
        string midtrans_merchant_id
        string stripe_publishable_key
        string stripe_secret_key
        string callback_finish_url
        string callback_unfinish_url
        string callback_error_url
        string notification_url
        string recurring_notification_url
        string account_linking_url
        datetime created_at
        datetime updated_at
    }

    MidtransTransaction {
        int id PK
        int order_id FK
        string transaction_id UK
        decimal gross_amount
        string payment_type
        string transaction_status
        string fraud_status
        datetime settlement_time
        string snap_token
        string snap_redirect_url
        text midtrans_response
        datetime created_at
        datetime updated_at
    }

    RestockOrder {
        int id PK
        int supplier_id FK
        string status
        decimal total_amount
        text notes
        datetime order_date
        datetime expected_date
        datetime received_date
        int created_by FK
        datetime created_at
    }

    RestockOrderItem {
        int id PK
        int restock_order_id FK
        int product_id FK
        int quantity_ordered
        int quantity_received
        decimal unit_cost
    }

    StoreProfile {
        int id PK
        string store_name
        string store_tagline
        text store_address
        string store_city
        string store_postal_code
        string store_phone
        string store_email
        string store_website
        string branch_name
        string branch_code
        string branch_manager
        string business_license
        string tax_number
        string logo_url
        string primary_color
        string secondary_color
        text operating_hours
        string facebook_url
        string instagram_url
        string whatsapp_number
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    ChatRoom {
        int id PK
        string name UK
        int buyer_id FK
        string buyer_name
        string buyer_email
        boolean is_active
        datetime created_at
    }

    ChatMessage {
        int id PK
        int room_id FK
        int user_id FK
        string user_name
        string user_email
        text message
        string sender_type
        int product_id FK
        boolean is_read
        boolean is_deleted
        datetime created_at
        datetime updated_at
    }

    ChatSession {
        int id PK
        int room_id FK
        int user_id FK
        string user_name
        string user_email
        string user_role
        datetime started_at
        datetime ended_at
        boolean is_active
    }

    %% Relationships
    User ||--o{ CartItem : has
    User ||--o{ Order : creates
    User ||--o{ RestockOrder : creates
    User ||--o{ ChatRoom : owns
    User ||--o{ ChatMessage : sends
    User ||--o{ ChatSession : participates

    Category ||--o{ Product : contains
    Supplier ||--o{ Product : supplies

    Product ||--o{ ProductImage : has
    Product ||--o{ CartItem : added_to
    Product ||--o{ OrderItem : ordered_in
    Product ||--o{ RestockOrderItem : restocked_in
    Product ||--o{ ChatMessage : tagged_in

    Order ||--o{ OrderItem : contains
    Order ||--o{ MidtransTransaction : processed_by
    ShippingService ||--o{ Order : ships

    RestockOrder ||--o{ RestockOrderItem : contains
    Supplier ||--o{ RestockOrder : supplies

    ChatRoom ||--o{ ChatMessage : contains
    ChatRoom ||--o{ ChatSession : hosts
```

---

## 📊 Data Flow Diagram (DFD)

### Level 0 - Context Diagram

```mermaid
graph TD
    Customer[👤 Customer]
    Admin[👨‍💼 Admin/Staff]
    System[🎸 HURTROCK MUSIC STORE SYSTEM]
    PaymentGateway[💳 Payment Gateway<br/>Stripe/Midtrans]
    CourierServices[🚚 Courier Services<br/>JNE/J&T/SiCepat]
    EmailService[📧 Email Service]
    ChatService[💬 Chat Service]

    Customer -->|Browse Products<br/>Place Orders<br/>Make Payments<br/>Chat Support| System
    Admin -->|Manage Products<br/>Process Orders<br/>View Analytics<br/>Handle Chat| System

    System -->|Product Info<br/>Order Status<br/>Payment Confirmation<br/>Chat Messages| Customer
    System -->|Reports<br/>Dashboards<br/>Notifications<br/>Chat Management| Admin

    System -->|Payment Request| PaymentGateway
    System -->|Shipping Request| CourierServices
    System -->|Email Notifications| EmailService
    System -.->|Real-time Chat| ChatService

    PaymentGateway -->|Payment Response<br/>Transaction Status| System
    CourierServices -->|Shipping Status<br/>Tracking Info| System
    EmailService -->|Delivery Status| System
    ChatService -.->|Chat Messages<br/>User Status| System
```

### Level 1 - System Decomposition

```mermaid
graph TD
    Customer[👤 Customer]
    AdminUser[👨‍💼 Admin User]

    subgraph "Main System Processes"
        P1[1.0<br/>User Authentication<br/>& Management]
        P2[2.0<br/>Product Catalog<br/>Management]
        P3[3.0<br/>Shopping Cart<br/>Management]
        P4[4.0<br/>Order Processing<br/>& Fulfillment]
        P5[5.0<br/>Payment Processing<br/>& Gateway Integration]
        P6[6.0<br/>Inventory<br/>Management]
        P7[7.0<br/>Reporting<br/>& Analytics]
        P8[8.0<br/>Real-time Chat<br/>Support]
    end

    subgraph "Data Stores"
        D1[(D1: User Database)]
        D2[(D2: Product Database)]
        D3[(D3: Category Database)]
        D4[(D4: Order Database)]
        D5[(D5: Payment Database)]
        D6[(D6: Inventory Database)]
        D7[(D7: Analytics Database)]
        D8[(D8: Chat Database)]
    end

    subgraph "External Entities"
        EXT1[Payment Gateway]
        EXT2[Courier Services]
        EXT3[Email Service]
    end

    %% Customer flows
    Customer --> P1
    Customer --> P2
    Customer --> P3
    Customer --> P4
    Customer --> P8

    %% Admin flows
    AdminUser --> P1
    AdminUser --> P2
    AdminUser --> P4
    AdminUser --> P6
    AdminUser --> P7
    AdminUser --> P8

    %% Process to data store flows
    P1 --> D1
    P2 --> D2
    P2 --> D3
    P3 --> D2
    P4 --> D4
    P4 --> D2
    P5 --> D5
    P6 --> D6
    P7 --> D7
    P8 --> D8

    %% External system flows
    P5 --> EXT1
    P4 --> EXT2
    P4 --> EXT3

    EXT1 --> P5
    EXT2 --> P4
    EXT3 --> P4
```

### Level 2 - Order Processing Detail

```mermaid
graph TD
    Customer[👤 Customer]

    subgraph "Order Processing (Process 4.0)"
        P41[4.1<br/>Validate Order<br/>& Stock Check]
        P42[4.2<br/>Calculate Shipping<br/>& Total Cost]
        P43[4.3<br/>Process Payment<br/>Authorization]
        P44[4.4<br/>Create Order<br/>Record]
        P45[4.5<br/>Update Inventory<br/>Stock Levels]
        P46[4.6<br/>Generate Shipping<br/>Label & Tracking]
        P47[4.7<br/>Send Order<br/>Confirmation]
        P48[4.8<br/>Update Order<br/>Status]
    end

    subgraph "Data Stores"
        D2[(D2: Product Database)]
        D4[(D4: Order Database)]
        D5[(D5: Payment Database)]
        D6[(D6: Inventory Database)]
    end

    subgraph "External Systems"
        PaymentGW[Payment Gateway]
        CourierAPI[Courier API]
        EmailSys[Email System]
    end

    Customer --> P41
    P41 --> D2
    P41 --> P42
    P42 --> P43
    P43 --> PaymentGW
    PaymentGW --> P43
    P43 --> P44
    P44 --> D4
    P44 --> P45
    P45 --> D6
    P45 --> P46
    P46 --> CourierAPI
    P46 --> P47
    P47 --> EmailSys
    P47 --> P48
    P48 --> D4
```

---

## 👥 Use Case Diagram

### Complete System Use Cases

```mermaid
graph TB
    subgraph "Actors"
        Customer[👤 Customer<br/>Buyer Role]
        Admin[👨‍💼 Admin<br/>Admin Role]
        Staff[👩‍💼 Staff<br/>Staff Role]
        PaymentGW[💳 Payment Gateway]
        CourierSys[🚚 Courier System]
    end

    subgraph "Customer Use Cases"
        UC1[Browse Products & Categories]
        UC2[Search Products]
        UC3[View Product Details]
        UC4[Manage Shopping Cart]
        UC5[User Registration & Login]
        UC6[Manage User Profile]
        UC7[Checkout & Payment]
        UC8[Track Orders]
        UC9[View Order History]
        UC10[Switch Light/Dark Theme]
        UC11[Chat with Support]
        UC12[Rate & Review Products]
    end

    subgraph "Admin Use Cases"
        UC13[Manage Products & Categories]
        UC14[Upload Product Images]
        UC15[Manage Users & Roles]
        UC16[Process Orders]
        UC17[Update Order Status]
        UC18[Generate Shipping Labels]
        UC19[View Analytics & Reports]
        UC20[Export Sales Data]
        UC21[Manage Suppliers]
        UC22[Manage Payment Config]
        UC23[Manage Shipping Services]
        UC24[Configure Store Profile]
        UC25[Handle Chat Support]
        UC26[Inventory Management]
        UC27[Restock Orders]
    end

    subgraph "Staff Use Cases"
        UC28[View Orders]
        UC29[Update Order Status]
        UC30[Print Shipping Labels]
        UC31[View Basic Analytics]
        UC32[Handle Customer Chat]
    end

    subgraph "System Integration"
        UC33[Process Payment]
        UC34[Send Payment Notifications]
        UC35[Calculate Shipping Cost]
        UC36[Track Package Status]
        UC37[Send Email Notifications]
    end

    %% Customer connections
    Customer --> UC1
    Customer --> UC2
    Customer --> UC3
    Customer --> UC4
    Customer --> UC5
    Customer --> UC6
    Customer --> UC7
    Customer --> UC8
    Customer --> UC9
    Customer --> UC10
    Customer --> UC11
    Customer --> UC12

    %% Admin connections
    Admin --> UC13
    Admin --> UC14
    Admin --> UC15
    Admin --> UC16
    Admin --> UC17
    Admin --> UC18
    Admin --> UC19
    Admin --> UC20
    Admin --> UC21
    Admin --> UC22
    Admin --> UC23
    Admin --> UC24
    Admin --> UC25
    Admin --> UC26
    Admin --> UC27

    %% Staff connections  
    Staff --> UC28
    Staff --> UC29
    Staff --> UC30
    Staff --> UC31
    Staff --> UC32

    %% External system connections
    UC7 --> UC33
    PaymentGW --> UC34
    UC7 --> UC35
    CourierSys --> UC36
    UC17 --> UC37

    %% Use case dependencies
    UC4 --> UC7
    UC7 --> UC8
    UC33 --> UC16
    UC16 --> UC17
    UC17 --> UC18
```

---

## 🛍️ Customer Journey Flowchart

### Complete Customer Experience Flow

```mermaid
flowchart TD
    Start([👤 Customer Arrives])

    %% Initial Landing
    Landing{Browse Homepage}
    Register[📝 Register New Account]
    Login[🔐 Login Existing Account]
    GuestBrowse[👁️ Browse as Guest]

    %% Product Discovery
    SearchProduct[🔍 Search Products]
    BrowseCategory[📂 Browse by Category]
    ViewFeatured[⭐ View Featured Products]

    %% Product Selection
    ProductDetail[📱 View Product Details]
    CheckStock{Stock Available?}
    OutOfStock[❌ Out of Stock Notice]
    AddToCart[🛒 Add to Cart]
    ContinueShopping{Continue Shopping?}

    %% Cart Management
    ViewCart[🛒 View Shopping Cart]
    UpdateCart[✏️ Update Quantities]
    RemoveItems[🗑️ Remove Items]
    CartEmpty{Cart Empty?}

    %% Checkout Process
    ProceedCheckout[💳 Proceed to Checkout]
    CheckProfile{Profile Complete?}
    UpdateProfile[📋 Update Profile Info]
    SelectShipping[🚚 Select Shipping Method]
    ReviewOrder[📋 Review Order Details]
    SelectPayment[💰 Select Payment Method]

    %% Payment Processing
    ProcessPayment[⏳ Process Payment]
    PaymentSuccess{Payment Success?}
    PaymentFailed[❌ Payment Failed]
    RetryPayment{Retry Payment?}

    %% Order Completion
    OrderConfirm[✅ Order Confirmation]
    ReceiveEmail[📧 Confirmation Email]
    TrackOrder[📦 Track Order Status]

    %% Post-Purchase
    OrderDelivered{Order Delivered?}
    RateReview[⭐ Rate & Review]
    ContactSupport[💬 Contact Support]

    %% Chat Support (Available Throughout)
    ChatSupport[💬 Live Chat Support]

    End([🎉 Customer Journey Complete])

    %% Flow connections
    Start --> Landing

    Landing --> Register
    Landing --> Login
    Landing --> GuestBrowse

    Register --> SearchProduct
    Login --> SearchProduct
    GuestBrowse --> SearchProduct

    SearchProduct --> ProductDetail
    BrowseCategory --> ProductDetail
    ViewFeatured --> ProductDetail

    ProductDetail --> CheckStock
    CheckStock -->|❌ No| OutOfStock
    CheckStock -->|✅ Yes| AddToCart
    OutOfStock --> ContinueShopping

    AddToCart --> ContinueShopping
    ContinueShopping -->|Yes| SearchProduct
    ContinueShopping -->|No| ViewCart

    ViewCart --> UpdateCart
    ViewCart --> RemoveItems
    ViewCart --> ProceedCheckout
    UpdateCart --> CartEmpty
    RemoveItems --> CartEmpty

    CartEmpty -->|Yes| SearchProduct
    CartEmpty -->|No| ViewCart

    ProceedCheckout --> CheckProfile
    CheckProfile -->|❌ Incomplete| UpdateProfile
    CheckProfile -->|✅ Complete| SelectShipping
    UpdateProfile --> SelectShipping

    SelectShipping --> ReviewOrder
    ReviewOrder --> SelectPayment
    SelectPayment --> ProcessPayment

    ProcessPayment --> PaymentSuccess
    PaymentSuccess -->|❌ Failed| PaymentFailed
    PaymentSuccess -->|✅ Success| OrderConfirm

    PaymentFailed --> RetryPayment
    RetryPayment -->|Yes| SelectPayment
    RetryPayment -->|No| ViewCart

    OrderConfirm --> ReceiveEmail
    ReceiveEmail --> TrackOrder

    TrackOrder --> OrderDelivered
    OrderDelivered -->|❌ No| TrackOrder
    OrderDelivered -->|✅ Yes| RateReview

    RateReview --> End
    ContactSupport --> End

    %% Chat support can be accessed from anywhere
    Landing -.->|Help Needed| ChatSupport
    ProductDetail -.->|Product Questions| ChatSupport
    ViewCart -.->|Cart Issues| ChatSupport
    ProceedCheckout -.->|Checkout Help| ChatSupport
    PaymentFailed -.->|Payment Issues| ChatSupport
    TrackOrder -.->|Order Questions| ChatSupport

    ChatSupport -.-> End

    %% Theme switching available throughout
    Landing -.->|🌓 Theme Toggle| Landing
```

### Customer State Transitions

```mermaid
stateDiagram-v2
    [*] --> Anonymous
    Anonymous --> Registered : Register
    Anonymous --> LoggedIn : Login
    Anonymous --> Browsing : Browse as Guest

    Registered --> LoggedIn : Auto-login
    LoggedIn --> Browsing : Start Shopping

    state Browsing {
        [*] --> ViewingProducts
        ViewingProducts --> SearchingProducts : Search
        SearchingProducts --> ViewingProducts : View Results
        ViewingProducts --> ViewingProductDetail : Select Product
        ViewingProductDetail --> ViewingProducts : Back to Catalog
    }

    Browsing --> Shopping : Add to Cart

    state Shopping {
        [*] --> ManagingCart
        ManagingCart --> ReviewingCart : View Cart
        ReviewingCart --> ManagingCart : Update Items
        ReviewingCart --> CheckingOut : Proceed to Checkout
    }

    Shopping --> Browsing : Continue Shopping
    Shopping --> CheckingOut : Ready to Purchase

    state CheckingOut {
        [*] --> ValidatingProfile
        ValidatingProfile --> SelectingShipping : Profile OK
        ValidatingProfile --> UpdatingProfile : Profile Incomplete
        UpdatingProfile --> SelectingShipping : Profile Updated
        SelectingShipping --> ReviewingOrder : Shipping Selected
        ReviewingOrder --> ProcessingPayment : Confirm Order
    }

    state ProcessingPayment {
        [*] --> PaymentPending
        PaymentPending --> PaymentSuccess : Payment Approved
        PaymentPending --> PaymentFailed : Payment Declined
        PaymentFailed --> PaymentRetry : Retry
        PaymentRetry --> PaymentPending : New Payment Attempt
    }

    CheckingOut --> ProcessingPayment : Submit Payment
    ProcessingPayment --> OrderConfirmed : Payment Success
    ProcessingPayment --> Shopping : Payment Failed (Retry Later)

    OrderConfirmed --> TrackingOrder : Order Placed

    state TrackingOrder {
        [*] --> OrderPending
        OrderPending --> OrderPaid : Payment Confirmed
        OrderPaid --> OrderShipped : Shipped
        OrderShipped --> OrderDelivered : Delivered
        OrderDelivered --> OrderCompleted : Customer Satisfied
    }

    TrackingOrder --> [*] : Order Complete
    LoggedIn --> [*] : Logout
    Anonymous --> [*] : Leave Site
```

---

## 👨‍💼 Admin Workflow Flowchart

### Admin Dashboard Flow

```mermaid
flowchart TD
    AdminLogin[🔐 Admin Login]
    Dashboard[📊 Admin Dashboard]

    subgraph "Main Admin Functions"
        ProductMgmt[📦 Product Management]
        OrderMgmt[📋 Order Management]
        UserMgmt[👥 User Management]
        Analytics[📈 Analytics & Reports]
        Settings[⚙️ System Settings]
        ChatMgmt[💬 Chat Management]
        InventoryMgmt[📦 Inventory Management]
    end

    AdminLogin --> Dashboard
    Dashboard --> ProductMgmt
    Dashboard --> OrderMgmt
    Dashboard --> UserMgmt
    Dashboard --> Analytics
    Dashboard --> Settings
    Dashboard --> ChatMgmt
    Dashboard --> InventoryMgmt
```

### Product Management Flow

```mermaid
flowchart TD
    ProductMgmt[📦 Product Management]
    ViewProducts[👁️ View All Products]

    subgraph "Product Actions"
        CreateProduct[➕ Create New Product]
        EditProduct[✏️ Edit Product]
        DeleteProduct[🗑️ Delete Product]
        ManageImages[🖼️ Manage Images]
        SetFeatured[⭐ Set Featured]
        UpdateStock[📦 Update Stock]
    end

    subgraph "Create Product Flow"
        FillBasicInfo[📝 Fill Basic Info]
        SelectCategory[📂 Select Category]
        SetPricing[💰 Set Pricing]
        AddImages[🖼️ Add Product Images]
        SetDimensions[📏 Set Dimensions/Weight]
        SetStockLevels[📦 Set Stock Levels]
        SetSupplier[🏢 Set Supplier Info]
        SaveProduct[💾 Save Product]
    end

    subgraph "Image Management"
        UploadImages[📤 Upload New Images]
        SelectThumbnail[🖼️ Select Thumbnail]
        ReorderImages[🔄 Reorder Images]
        DeleteImages[🗑️ Delete Images]
        CompressImages[🗜️ Auto Compress]
    end

    subgraph "Stock Management"
        CheckStockLevels[📊 Check Stock Levels]
        LowStockAlert[⚠️ Low Stock Alert]
        CriticalStockAlert[🚨 Critical Stock Alert]
        CreateRestockOrder[📋 Create Restock Order]
        UpdateMinimumStock[📦 Update Minimum Stock]
    end

    ProductMgmt --> ViewProducts
    ViewProducts --> CreateProduct
    ViewProducts --> EditProduct
    ViewProducts --> DeleteProduct
    ViewProducts --> ManageImages
    ViewProducts --> SetFeatured
    ViewProducts --> UpdateStock

    CreateProduct --> FillBasicInfo
    FillBasicInfo --> SelectCategory
    SelectCategory --> SetPricing
    SetPricing --> AddImages
    AddImages --> SetDimensions
    SetDimensions --> SetStockLevels
    SetStockLevels --> SetSupplier
    SetSupplier --> SaveProduct

    ManageImages --> UploadImages
    ManageImages --> SelectThumbnail
    ManageImages --> ReorderImages
    ManageImages --> DeleteImages
    UploadImages --> CompressImages

    UpdateStock --> CheckStockLevels
    CheckStockLevels --> LowStockAlert
    CheckStockLevels --> CriticalStockAlert
    LowStockAlert --> CreateRestockOrder
    CriticalStockAlert --> CreateRestockOrder
    CheckStockLevels --> UpdateMinimumStock

    SaveProduct --> ViewProducts
    CreateRestockOrder --> ViewProducts
```

### Order Management Flow

```mermaid
flowchart TD
    OrderMgmt[📋 Order Management]
    ViewOrders[👁️ View All Orders]

    subgraph "Order Statuses"
        PendingOrders[⏳ Pending Orders]
        PaidOrders[💰 Paid Orders]
        ShippedOrders[🚚 Shipped Orders]
        DeliveredOrders[✅ Delivered Orders]
        CancelledOrders[❌ Cancelled Orders]
    end

    subgraph "Order Actions"
        ViewOrderDetails[🔍 View Order Details]
        UpdateOrderStatus[🔄 Update Status]
        PrintShippingLabel[🏷️ Print Shipping Label]
        AddTrackingNumber[📍 Add Tracking Number]
        ProcessRefund[💸 Process Refund]
        ContactCustomer[📧 Contact Customer]
        GenerateInvoice[📄 Generate Invoice]
    end

    subgraph "Shipping Process"
        ValidateAddress[📍 Validate Address]
        SelectCourier[🚚 Select Courier Service]
        CalculateShipping[💰 Calculate Shipping Cost]
        GenerateLabel[🏷️ Generate Shipping Label]
        CreateTrackingNumber[📍 Create Tracking Number]
        NotifyCustomer[📧 Notify Customer]
        UpdateStatus[🔄 Update to Shipped]
    end

    subgraph "Quick Actions"
        QuickShip[🚀 Quick Ship]
        BulkStatusUpdate[📦 Bulk Status Update]
        ExportOrders[📤 Export Orders]
        PrintBatch[🖨️ Print Batch Labels]
    end

    OrderMgmt --> ViewOrders
    ViewOrders --> PendingOrders
    ViewOrders --> PaidOrders
    ViewOrders --> ShippedOrders
    ViewOrders --> DeliveredOrders
    ViewOrders --> CancelledOrders

    ViewOrders --> ViewOrderDetails
    ViewOrderDetails --> UpdateOrderStatus
    ViewOrderDetails --> PrintShippingLabel
    ViewOrderDetails --> AddTrackingNumber
    ViewOrderDetails --> ProcessRefund
    ViewOrderDetails --> ContactCustomer
    ViewOrderDetails --> GenerateInvoice

    PaidOrders --> ValidateAddress
    ValidateAddress --> SelectCourier
    SelectCourier --> CalculateShipping
    CalculateShipping --> GenerateLabel
    GenerateLabel --> CreateTrackingNumber
    CreateTrackingNumber --> NotifyCustomer
    NotifyCustomer --> UpdateStatus

    ViewOrders --> QuickShip
    ViewOrders --> BulkStatusUpdate
    ViewOrders --> ExportOrders
    ViewOrders --> PrintBatch
```

---

## 📋 Order Processing Flowchart

### Complete Order Lifecycle

```mermaid
flowchart TD
    OrderReceived([📝 New Order Received])

    subgraph "Order Validation"
        ValidateOrder[🔍 Validate Order Data]
        CheckCustomer[👤 Verify Customer Info]
        ValidateItems[📦 Validate Order Items]
        OrderValid{Order Valid?}
        RejectOrder[❌ Reject Order]
        SendRejectionEmail[📧 Send Rejection Email]
    end

    subgraph "Stock Verification"
        CheckStock[📦 Check Stock Availability]
        StockAvailable{All Items Available?}
        ReserveStock[📌 Reserve Stock Items]
        PartialStock[⚠️ Partial Stock Available]
        BackorderItems[📋 Create Backorder]
        NotifyStockIssue[📧 Notify Stock Issues]
    end

    subgraph "Payment Processing"
        ValidatePayment[💳 Validate Payment Method]
        ProcessPayment[⏳ Process Payment]
        PaymentSuccess{Payment Successful?}
        PaymentFailed[❌ Payment Failed]
        NotifyPaymentFailure[📧 Payment Failure Notice]
        ConfirmPayment[✅ Confirm Payment]
        UpdateOrderStatus1[📊 Status: Paid]
    end

    subgraph "Order Fulfillment"
        GenerateInvoice[📄 Generate Invoice]
        AllocateInventory[📦 Allocate Inventory]
        PreparePackaging[📦 Prepare for Packaging]
        PackageOrder[📦 Package Items]
        WeighPackage[⚖️ Weigh Package]
        SelectCourier[🚚 Select Courier Service]
        GenerateShippingLabel[🏷️ Generate Shipping Label]
        CreateTrackingNumber[📍 Create Tracking Number]
        UpdateOrderStatus2[📊 Status: Shipped]
    end

    subgraph "Shipping & Delivery"
        HandoverToCourier[🚚 Handover to Courier]
        NotifyCustomerShipped[📧 Shipping Notification]
        TrackPackage[📍 Track Package Movement]
        UpdateDeliveryStatus[🔄 Update Delivery Status]
        PackageDelivered{Package Delivered?}
        DeliveryConfirmed[✅ Delivery Confirmed]
        UpdateOrderStatus3[📊 Status: Delivered]
        DeliveryFailed[❌ Delivery Failed]
        RetryDelivery[🔄 Schedule Retry]
        ContactCustomerDelivery[📧 Contact Customer]
    end

    subgraph "Post-Delivery"
        SendCompletionEmail[📧 Order Completion Email]
        RequestFeedback[⭐ Request Customer Feedback]
        ArchiveOrder[📁 Archive Order]
        UpdateAnalytics[📊 Update Sales Analytics]
        OrderComplete[✅ Order Complete]
    end

    subgraph "Exception Handling"
        OrderCancelled[❌ Order Cancelled]
        ProcessRefund[💸 Process Refund]
        RestoreStock[📦 Restore Stock Levels]
        NotifyCancellation[📧 Cancellation Notice]
    end

    OrderReceived --> ValidateOrder
    ValidateOrder --> CheckCustomer
    CheckCustomer --> ValidateItems
    ValidateItems --> OrderValid

    OrderValid -->|❌ Invalid| RejectOrder
    RejectOrder --> SendRejectionEmail
    SendRejectionEmail --> OrderComplete

    OrderValid -->|✅ Valid| CheckStock
    CheckStock --> StockAvailable

    StockAvailable -->|❌ Insufficient| PartialStock
    PartialStock --> BackorderItems
    BackorderItems --> NotifyStockIssue
    NotifyStockIssue --> OrderCancelled

    StockAvailable -->|✅ Available| ReserveStock
    ReserveStock --> ValidatePayment
    ValidatePayment --> ProcessPayment
    ProcessPayment --> PaymentSuccess

    PaymentSuccess -->|❌ Failed| PaymentFailed
    PaymentFailed --> NotifyPaymentFailure
    NotifyPaymentFailure --> OrderCancelled

    PaymentSuccess -->|✅ Success| ConfirmPayment
    ConfirmPayment --> UpdateOrderStatus1
    UpdateOrderStatus1 --> GenerateInvoice

    GenerateInvoice --> AllocateInventory
    AllocateInventory --> PreparePackaging
    PreparePackaging --> PackageOrder
    PackageOrder --> WeighPackage
    WeighPackage --> SelectCourier
    SelectCourier --> GenerateShippingLabel
    GenerateShippingLabel --> CreateTrackingNumber
    CreateTrackingNumber --> UpdateOrderStatus2

    UpdateOrderStatus2 --> HandoverToCourier
    HandoverToCourier --> NotifyCustomerShipped
    NotifyCustomerShipped --> TrackPackage
    TrackPackage --> UpdateDeliveryStatus
    UpdateDeliveryStatus --> PackageDelivered

    PackageDelivered -->|❌ Failed| DeliveryFailed
    DeliveryFailed --> RetryDelivery
    RetryDelivery --> ContactCustomerDelivery
    ContactCustomerDelivery --> TrackPackage

    PackageDelivered -->|✅ Success| DeliveryConfirmed
    DeliveryConfirmed --> UpdateOrderStatus3
    UpdateOrderStatus3 --> SendCompletionEmail
    SendCompletionEmail --> RequestFeedback
    RequestFeedback --> ArchiveOrder
    ArchiveOrder --> UpdateAnalytics
    UpdateAnalytics --> OrderComplete

    OrderCancelled --> ProcessRefund
    ProcessRefund --> RestoreStock
    RestoreStock --> NotifyCancellation
    NotifyCancellation --> OrderComplete

    OrderComplete --> End([🏁 Process End])
```

---

## 💳 Payment Processing Flowchart

### Multi-Gateway Payment Flow

```mermaid
flowchart TD
    InitiatePayment([💳 Initiate Payment])

    subgraph "Payment Configuration"
        GetActiveConfig[⚙️ Get Active Payment Config]
        ConfigExists{Config Available?}
        NoConfigError[❌ No Payment Config Available]
        SelectGateway[🎯 Select Payment Gateway]
        GatewayType{Gateway Type?}
    end

    subgraph "Stripe Payment Flow"
        StripeConfig[🟦 Stripe Configuration]
        CreateStripeSession[📝 Create Checkout Session]
        BuildLineItems[📋 Build Line Items]
        AddShipping[🚚 Add Shipping Cost]
        CreateSession[✨ Create Stripe Session]
        RedirectToStripe[🔗 Redirect to Stripe]
        StripeCallback[↩️ Stripe Callback]
        StripeWebhook[🔔 Stripe Webhook]
    end

    subgraph "Midtrans Payment Flow"
        MidtransConfig[🟨 Midtrans Configuration]
        GenerateOrderID[🆔 Generate Order ID]
        BuildItemDetails[📋 Build Item Details]
        SetCustomerDetails[👤 Set Customer Details]
        CreateTransaction[💼 Create Snap Transaction]
        GetSnapToken[🎫 Get Snap Token]
        RedirectToMidtrans[🔗 Redirect to Midtrans]
        MidtransCallback[↩️ Midtrans Callback]
        MidtransWebhook[🔔 Midtrans Notification]
    end

    subgraph "Payment Verification"
        VerifyPayment[🔍 Verify Payment Status]
        UpdateTransactionRecord[📝 Update Transaction Record]
        PaymentSuccessful{Payment Successful?}
        HandleSuccess[✅ Handle Success]
        HandleFailure[❌ Handle Failure]
        UpdateOrderStatus[📊 Update Order Status]
    end

    subgraph "Post-Payment Processing"
        ClearCart[🛒 Clear Shopping Cart]
        CreateOrderItems[📦 Create Order Items]
        UpdateInventory[📦 Update Inventory]
        SendConfirmation[📧 Send Confirmation Email]
        RedirectToSuccess[🎉 Redirect to Success Page]
        LogTransaction[📝 Log Transaction Details]
    end

    subgraph "Error Handling"
        PaymentError[⚠️ Payment Error]
        LogError[📝 Log Error Details]
        NotifyCustomer[📧 Notify Customer]
        ReturnToCart[🛒 Return to Cart]
        OfferRetry[🔄 Offer Payment Retry]
    end

    InitiatePayment --> GetActiveConfig
    GetActiveConfig --> ConfigExists
    ConfigExists -->|❌ No| NoConfigError
    ConfigExists -->|✅ Yes| SelectGateway
    SelectGateway --> GatewayType

    %% Stripe Flow
    GatewayType -->|Stripe| StripeConfig
    StripeConfig --> CreateStripeSession
    CreateStripeSession --> BuildLineItems
    BuildLineItems --> AddShipping
    AddShipping --> CreateSession
    CreateSession --> RedirectToStripe
    RedirectToStripe --> StripeCallback
    StripeCallback --> VerifyPayment

    %% Midtrans Flow
    GatewayType -->|Midtrans| MidtransConfig
    MidtransConfig --> GenerateOrderID
    GenerateOrderID --> BuildItemDetails
    BuildItemDetails --> SetCustomerDetails
    SetCustomerDetails --> CreateTransaction
    CreateTransaction --> GetSnapToken
    GetSnapToken --> RedirectToMidtrans
    RedirectToMidtrans --> MidtransCallback
    MidtransCallback --> VerifyPayment

    %% Webhook Handling
    StripeWebhook --> UpdateTransactionRecord
    MidtransWebhook --> UpdateTransactionRecord

    %% Payment Verification
    VerifyPayment --> UpdateTransactionRecord
    UpdateTransactionRecord --> PaymentSuccessful

    PaymentSuccessful -->|✅ Success| HandleSuccess
    PaymentSuccessful -->|❌ Failed| HandleFailure

    HandleSuccess --> UpdateOrderStatus
    UpdateOrderStatus --> ClearCart
    ClearCart --> CreateOrderItems
    CreateOrderItems --> UpdateInventory
    UpdateInventory --> SendConfirmation
    SendConfirmation --> RedirectToSuccess
    RedirectToSuccess --> LogTransaction

    HandleFailure --> PaymentError
    PaymentError --> LogError
    LogError --> NotifyCustomer
    NotifyCustomer --> ReturnToCart
    ReturnToCart --> OfferRetry

    NoConfigError --> PaymentError
    OfferRetry --> SelectGateway

    LogTransaction --> End([🏁 Payment Complete])
    OfferRetry --> End
```

### Payment Status State Machine

```mermaid
stateDiagram-v2
    [*] --> PaymentInitiated
    PaymentInitiated --> PaymentPending : Create Session
    PaymentPending --> PaymentProcessing : User Submits

    state PaymentProcessing {
        [*] --> GatewayValidation
        GatewayValidation --> FraudCheck : Valid
        GatewayValidation --> ValidationFailed : Invalid
        FraudCheck --> AuthorizationCheck : Pass
        FraudCheck --> FraudDetected : Fail
        AuthorizationCheck --> PaymentApproved : Approved
        AuthorizationCheck --> InsufficientFunds : Declined
    }

    PaymentProcessing --> PaymentCompleted : Success
    PaymentProcessing --> PaymentFailed : Error
    PaymentProcessing --> PaymentCancelled : User Cancel

    PaymentFailed --> PaymentRetry : Retry
    PaymentRetry --> PaymentPending : New Attempt

    PaymentCompleted --> [*]
    PaymentFailed --> [*]
    PaymentCancelled --> [*]
```

---

## 🔐 Authentication Flow

### User Authentication Process

```mermaid
flowchart TD
    UserAccess[👤 User Access Request]
    CheckAuth{Authenticated?}

    subgraph "Login Process"
        LoginForm[📝 Login Form]
        ValidateCredentials[🔍 Validate Credentials]
        CheckPassword{Password Correct?}
        CheckUserActive{User Active?}
        CreateSession[📋 Create User Session]
        SetLoginCookies[🍪 Set Login Cookies]
        LoginSuccess[✅ Login Success]
        LoginFailed[❌ Login Failed]
    end

    subgraph "Registration Process"
        RegisterForm[📝 Registration Form]
        ValidateInput[🔍 Validate Input Data]
        CheckEmailExists{Email Exists?}
        HashPassword[🔒 Hash Password]
        CreateUser[👤 Create User Record]
        SendWelcomeEmail[📧 Send Welcome Email]
        AutoLogin[🔐 Auto Login New User]
        RegistrationSuccess[✅ Registration Success]
        RegistrationFailed[❌ Registration Failed]
    end

    subgraph "Session Management"
        CheckSession[🔍 Check Session Validity]
        SessionValid{Session Valid?}
        RefreshSession[🔄 Refresh Session]
        InvalidateSession[❌ Invalidate Session]
        RequireReauth[🔐 Require Re-authentication]
    end

    subgraph "Role-Based Access"
        CheckRole[👤 Check User Role]
        RoleType{Role Type?}
        AdminAccess[👨‍💼 Admin Access]
        StaffAccess[👩‍💼 Staff Access]
        BuyerAccess[👤 Buyer Access]
        AccessDenied[❌ Access Denied]
    end

    subgraph "Security Features"
        CSRFProtection[🛡️ CSRF Token Validation]
        PasswordHashing[🔒 Secure Password Storage]
        SessionSecurity[🔐 Secure Session Cookies]
        HTTPSEnforcement[🔒 HTTPS Enforcement]
    end

    UserAccess --> CheckAuth
    CheckAuth -->|❌ No| LoginForm
    CheckAuth -->|✅ Yes| CheckSession

    LoginForm --> ValidateCredentials
    ValidateCredentials --> CheckPassword
    CheckPassword -->|❌ Invalid| LoginFailed
    CheckPassword -->|✅ Valid| CheckUserActive
    CheckUserActive -->|❌ Inactive| LoginFailed
    CheckUserActive -->|✅ Active| CreateSession
    CreateSession --> SetLoginCookies
    SetLoginCookies --> LoginSuccess

    LoginForm -.->|New User| RegisterForm
    RegisterForm --> ValidateInput
    ValidateInput --> CheckEmailExists
    CheckEmailExists -->|✅ Exists| RegistrationFailed
    CheckEmailExists -->|❌ New| HashPassword
    HashPassword --> CreateUser
    CreateUser --> SendWelcomeEmail
    SendWelcomeEmail --> AutoLogin
    AutoLogin --> RegistrationSuccess

    CheckSession --> SessionValid
    SessionValid -->|✅ Valid| CheckRole
    SessionValid -->|❌ Invalid| RequireReauth
    RequireReauth --> LoginForm

    CheckRole --> RoleType
    RoleType -->|Admin| AdminAccess
    RoleType -->|Staff| StaffAccess  
    RoleType -->|Buyer| BuyerAccess
    RoleType -->|Invalid| AccessDenied

    LoginSuccess --> CheckRole
    RegistrationSuccess --> BuyerAccess

    %% Security Implementations
    ValidateCredentials -.-> CSRFProtection
    CreateUser -.-> PasswordHashing
    CreateSession -.-> SessionSecurity
    UserAccess -.-> HTTPSEnforcement

    AdminAccess --> AuthorizedAccess[✅ Authorized Access]
    StaffAccess --> AuthorizedAccess
    BuyerAccess --> AuthorizedAccess

    LoginFailed --> LoginForm
    RegistrationFailed --> RegisterForm
    AccessDenied --> LoginForm

    AuthorizedAccess --> End([🎯 Access Granted])
```

---

## 🛒 Cart Management Flow

### Shopping Cart Operations

```mermaid
flowchart TD
    CartAccess[🛒 Access Cart]
    CheckUser{User Logged In?}
    RequireLogin[🔐 Require Login]

    subgraph "Add to Cart Flow"
        SelectProduct[📱 Select Product]
        CheckProductStock{Stock Available?}
        OutOfStock[❌ Out of Stock]
        ChooseQuantity[🔢 Choose Quantity]
        ValidateQuantity{Quantity Valid?}
        AddToCart[➕ Add to Cart]
        CheckExistingItem{Item in Cart?}
        UpdateQuantity[🔄 Update Quantity]
        CreateNewItem[✨ Create New Cart Item]
        ShowSuccess[✅ Added Successfully]
    end

    subgraph "View Cart Flow"
        LoadCartItems[📋 Load Cart Items]
        CheckCartEmpty{Cart Empty?}
        ShowEmptyCart[📭 Show Empty Cart]
        DisplayCartItems[📦 Display Cart Items]
        CalculateSubtotal[💰 Calculate Subtotal]
        ShowCartSummary[📊 Show Cart Summary]
    end

    subgraph "Update Cart Flow"
        ModifyQuantity[✏️ Modify Quantity]
        NewQuantityValid{Quantity > 0?}
        RemoveItem[🗑️ Remove Item]
        UpdateCartItem[🔄 Update Cart Item]
        RecalculateTotal[💰 Recalculate Total]
        UpdateDisplay[🔄 Update Display]
    end

    subgraph "Remove from Cart Flow"
        ConfirmRemoval{Confirm Remove?}
        DeleteCartItem[🗑️ Delete Cart Item]
        ShowRemovalMessage[📝 Show Removal Message]
    end

    subgraph "Clear Cart Flow"
        ConfirmClearAll{Clear All Items?}
        DeleteAllItems[🗑️ Delete All Items]
        ShowClearMessage[📝 Cart Cleared Message]
    end

    subgraph "Checkout Preparation"
        ValidateCartItems[🔍 Validate Cart Items]
        CheckAllStock{All Items Available?}
        StockIssues[⚠️ Stock Issues Found]
        UpdateStockInfo[📦 Update Stock Info]
        PrepareCheckout[✅ Prepare for Checkout]
    end

    CartAccess --> CheckUser
    CheckUser -->|❌ No| RequireLogin
    CheckUser -->|✅ Yes| LoadCartItems

    SelectProduct --> CheckProductStock
    CheckProductStock -->|❌ No| OutOfStock
    CheckProductStock -->|✅ Yes| ChooseQuantity
    ChooseQuantity --> ValidateQuantity
    ValidateQuantity -->|❌ Invalid| ChooseQuantity
    ValidateQuantity -->|✅ Valid| AddToCart
    AddToCart --> CheckExistingItem
    CheckExistingItem -->|✅ Exists| UpdateQuantity
    CheckExistingItem -->|❌ New| CreateNewItem
    UpdateQuantity --> ShowSuccess
    CreateNewItem --> ShowSuccess

    LoadCartItems --> CheckCartEmpty
    CheckCartEmpty -->|✅ Empty| ShowEmptyCart
    CheckCartEmpty -->|❌ Has Items| DisplayCartItems
    DisplayCartItems --> CalculateSubtotal
    CalculateSubtotal --> ShowCartSummary

    ShowCartSummary --> ModifyQuantity
    ModifyQuantity --> NewQuantityValid
    NewQuantityValid -->|❌ Zero| RemoveItem
    NewQuantityValid -->|✅ Positive| UpdateCartItem
    UpdateCartItem --> RecalculateTotal
    RecalculateTotal --> UpdateDisplay

    RemoveItem --> ConfirmRemoval
    ConfirmRemoval -->|✅ Yes| DeleteCartItem
    ConfirmRemoval -->|❌ No| ShowCartSummary
    DeleteCartItem --> ShowRemovalMessage
    ShowRemovalMessage --> RecalculateTotal

    ShowCartSummary --> ConfirmClearAll
    ConfirmClearAll -->|✅ Yes| DeleteAllItems
    ConfirmClearAll -->|❌ No| ShowCartSummary
    DeleteAllItems --> ShowClearMessage

    ShowCartSummary --> ValidateCartItems
    ValidateCartItems --> CheckAllStock
    CheckAllStock -->|❌ Issues| StockIssues
    CheckAllStock -->|✅ Available| PrepareCheckout
    StockIssues --> UpdateStockInfo
    UpdateStockInfo --> ShowCartSummary

    RequireLogin --> End([🔚 Login Required])
    OutOfStock --> End
    ShowSuccess --> End
    ShowEmptyCart --> End  
    UpdateDisplay --> End
    ShowClearMessage --> End
    PrepareCheckout --> CheckoutFlow[💳 Proceed to Checkout]

    CheckoutFlow --> End([🎯 Continue to Checkout])
```

---

## 📦 Inventory Management Flow

### Stock Management System

```mermaid
flowchart TD
    InventoryDashboard[📦 Inventory Dashboard]

    subgraph "Stock Monitoring"
        ViewAllProducts[👁️ View All Products]
        CheckStockLevels[📊 Check Stock Levels]
        StockStatus{Stock Status?}
        AdequateStock[✅ Adequate Stock]
        LowStock[⚠️ Low Stock Alert]
        CriticalStock[🚨 Critical Stock Alert]
        OutOfStock[❌ Out of Stock]
    end

    subgraph "Stock Alerts"
        GenerateAlerts[🚨 Generate Stock Alerts]
        NotifyManagement[📧 Notify Management]
        CreateAlertReport[📋 Create Alert Report]
        ScheduleRestock[📅 Schedule Restock]
    end

    subgraph "Restock Management"
        CreateRestockOrder[📝 Create Restock Order]
        SelectSupplier[🏢 Select Supplier]
        AddRestockItems[📦 Add Items to Restock]
        SetQuantities[🔢 Set Quantities]
        SetUnitCosts[💰 Set Unit Costs]
        CalculateTotal[💰 Calculate Total Cost]
        ReviewRestockOrder[👁️ Review Restock Order]
        SubmitRestockOrder[📤 Submit to Supplier]
        TrackRestockOrder[📍 Track Restock Order]
    end

    subgraph "Stock Receiving"
        ReceiveShipment[📦 Receive Shipment]
        VerifyItems[🔍 Verify Received Items]
        CheckQuantities{Quantities Match?}
        ReportDiscrepancy[⚠️ Report Discrepancy]
        UpdateInventory[📊 Update Inventory Levels]
        MarkRestockComplete[✅ Mark Restock Complete]
        GenerateReceiptReport[📋 Generate Receipt Report]
    end

    subgraph "Stock Adjustments"
        ManualAdjustment[✏️ Manual Stock Adjustment]
        AdjustmentReason[📝 Document Reason]
        AdjustmentTypes{Adjustment Type?}
        StockIncrease[➕ Stock Increase]
        StockDecrease[➖ Stock Decrease]
        DamageReport[💥 Damage Report]
        TheftReport[🚫 Theft Report]
        UpdateStockLevels[📊 Update Stock Levels]
        LogAdjustment[📝 Log Adjustment History]
    end

    subgraph "Inventory Reporting"
        GenerateStockReport[📊 Generate Stock Report]
        LowStockReport[⚠️ Low Stock Report]
        ValueReport[💰 Inventory Value Report]
        MovementReport[🔄 Stock Movement Report]
        ExportReports[📤 Export Reports]
    end

    InventoryDashboard --> ViewAllProducts
    ViewAllProducts --> CheckStockLevels
    CheckStockLevels --> StockStatus

    StockStatus --> AdequateStock
    StockStatus --> LowStock
    StockStatus --> CriticalStock
    StockStatus --> OutOfStock

    LowStock --> GenerateAlerts
    CriticalStock --> GenerateAlerts
    OutOfStock --> GenerateAlerts

    GenerateAlerts --> NotifyManagement
    NotifyManagement --> CreateAlertReport
    CreateAlertReport --> ScheduleRestock

    ScheduleRestock --> CreateRestockOrder
    CreateRestockOrder --> SelectSupplier
    SelectSupplier --> AddRestockItems
    AddRestockItems --> SetQuantities
    SetQuantities --> SetUnitCosts
    SetUnitCosts --> CalculateTotal
    CalculateTotal --> ReviewRestockOrder
    ReviewRestockOrder --> SubmitRestockOrder
    SubmitRestockOrder --> TrackRestockOrder

    TrackRestockOrder --> ReceiveShipment
    ReceiveShipment --> VerifyItems
    VerifyItems --> CheckQuantities
    CheckQuantities -->|❌ Mismatch| ReportDiscrepancy
    CheckQuantities -->|✅ Match| UpdateInventory
    ReportDiscrepancy --> UpdateInventory
    UpdateInventory --> MarkRestockComplete
    MarkRestockComplete --> GenerateReceiptReport

    InventoryDashboard --> ManualAdjustment
    ManualAdjustment --> AdjustmentReason
    AdjustmentReason --> AdjustmentTypes
    AdjustmentTypes --> StockIncrease
    AdjustmentTypes --> StockDecrease
    AdjustmentTypes --> DamageReport
    AdjustmentTypes --> TheftReport
    StockIncrease --> UpdateStockLevels
    StockDecrease --> UpdateStockLevels
    DamageReport --> UpdateStockLevels
    TheftReport --> UpdateStockLevels
    UpdateStockLevels --> LogAdjustment

    InventoryDashboard --> GenerateStockReport
    GenerateStockReport --> LowStockReport
    GenerateStockReport --> ValueReport
    GenerateStockReport --> MovementReport
    LowStockReport --> ExportReports
    ValueReport --> ExportReports
    MovementReport --> ExportReports

    AdequateStock --> End([✅ Stock Management Complete])
    GenerateReceiptReport --> End
    LogAdjustment --> End
    ExportReports --> End
```

---

## 💬 Chat System Flow

### Real-time Chat Architecture

```mermaid
graph TD
    subgraph "Flask Application (Port 5000)"
        FlaskApp[🎸 Flask Main App]
        AuthEndpoint[🔐 JWT Token Generation]
        ChatProxy[🔄 Chat API Proxy]
    end

    subgraph "Django Chat Service (Port 8000)"
        DjangoApp[💬 Django Chat Service]
        WebSocketHandler[🔌 WebSocket Handler]
        ChatAPI[📡 Chat REST API]
        ChatModels[🗃️ Chat Models]
    end

    subgraph "Frontend Components"
        FloatingChat[💬 Floating Chat Widget]
        AdminChatInterface[👨‍💼 Admin Chat Interface]
        BuyerChatInterface[👤 Buyer Chat Interface]
    end

    subgraph "Database Layer"
        PostgresDB[(📊 PostgreSQL<br/>Main Database)]
        ChatDB[(💬 SQLite<br/>Chat Database)]
    end

    FlaskApp --> AuthEndpoint
    FlaskApp --> ChatProxy

    AuthEndpoint --> FloatingChat
    ChatProxy --> DjangoApp

    DjangoApp --> WebSocketHandler
    DjangoApp --> ChatAPI
    DjangoApp --> ChatModels

    FloatingChat --> WebSocketHandler
    AdminChatInterface --> WebSocketHandler
    BuyerChatInterface --> WebSocketHandler

    FloatingChat --> ChatAPI
    AdminChatInterface --> ChatAPI
    BuyerChatInterface --> ChatAPI

    ChatModels --> ChatDB
    FlaskApp --> PostgresDB
```

### Chat Message Flow

```mermaid
sequenceDiagram
    participant B as Browser/Client
    participant F as Flask App
    participant D as Django Chat
    participant DB as Database
    participant WS as WebSocket

    B->>F: Request chat token
    F->>F: Generate JWT token
    F-->>B: Return token

    B->>D: Connect WebSocket with token
    D->>D: Verify JWT token
    D-->>B: Connection established

    B->>D: Send message
    D->>DB: Save message
    D->>WS: Broadcast to room
    WS-->>B: Deliver message

    Note over B,DB: Real-time bidirectional communication
```

## Media Upload Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Flask Upload API
    participant FS as File System
    participant D as Django Chat
    participant DB as PostgreSQL

    U->>F: POST /api/chat/upload-media
    F->>F: Validate file (size, type)
    F->>F: Generate unique filename
    F->>FS: Save to uploads/medias_sends/
    F-->>U: Return media_url, media_type, filename

    U->>D: Send message with media_data
    D->>DB: Save message with media fields
    D->>D: Broadcast to WebSocket room
    D-->>U: Confirm message saved

    Note over U,DB: Media files stored in filesystem, metadata in database
```

### Chat Room States

```mermaid
stateDiagram-v2
    [*] --> RoomCreated
    RoomCreated --> WaitingForCustomer : Customer Joins
    WaitingForCustomer --> ActiveChat : Admin Joins
    WaitingForCustomer --> CustomerOnly : Customer Active

    CustomerOnly --> ActiveChat : Admin Joins
    ActiveChat --> CustomerOnly : Admin Leaves
    ActiveChat --> AdminOnly : Customer Leaves

    AdminOnly --> ActiveChat : Customer Returns
    AdminOnly --> RoomIdle : Admin Leaves

    CustomerOnly --> RoomIdle : Customer Leaves
    RoomIdle --> WaitingForCustomer : Customer Returns
    RoomIdle --> AdminOnly : Admin Joins

    ActiveChat --> ChatResolved : Issue Resolved
    ChatResolved --> RoomClosed : Close Chat
    RoomClosed --> [*]

    state ActiveChat {
        [*] --> MessagesExchanged
        MessagesExchanged --> TypingIndicator
        TypingIndicator --> MessagesExchanged
        MessagesExchanged --> FileSharing
        FileSharing --> MessagesExchanged
    }
```

---

## ⚠️ Error Handling Flow

### Comprehensive Error Management

```mermaid
flowchart TD
    ErrorOccurred[⚠️ Error Occurred]

    subgraph "Error Classification"
        ClassifyError[🔍 Classify Error Type]
        ErrorType{Error Type?}
        ValidationError[📝 Validation Error]
        DatabaseError[🗄️ Database Error]
        PaymentError[💳 Payment Error]
        AuthenticationError[🔐 Auth Error]
        SystemError[🔧 System Error]
        NetworkError[🌐 Network Error]
    end

    subgraph "Validation Error Handling"
        ShowFieldErrors[📝 Show Field Errors]
        HighlightInvalidFields[🔴 Highlight Invalid Fields]
        ProvideCorrection[💡 Provide Correction Hints]
        ReturnToForm[↩️ Return to Form]
    end

    subgraph "Database Error Handling"
        LogDatabaseError[📝 Log Database Error]
        CheckConnection[🔍 Check DB Connection]
        RetryOperation[🔄 Retry Operation]
        ShowGenericError[⚠️ Show Generic Error Message]
        NotifyAdministrator[📧 Notify Administrator]
    end

    subgraph "Payment Error Handling"
        LogPaymentError[📝 Log Payment Error]
        ShowPaymentError[💳 Show Payment Error]
        OfferRetry[🔄 Offer Retry Payment]
        SuggestAlternative[💡 Suggest Alternative Payment]
        ContactSupport[📞 Contact Support Option]
    end

    subgraph "Authentication Error Handling"
        LogSecurityEvent[🔒 Log Security Event]
        ClearSession[🗑️ Clear Session]
        RedirectToLogin[🔐 Redirect to Login]
        ShowAuthError[⚠️ Show Auth Error]
        BlockSuspiciousActivity[🚫 Block Suspicious Activity]
    end

    subgraph "System Error Handling"
        LogSystemError[📝 Log System Error]
        CheckSystemHealth[💊 Check System Health]
        ShowMaintenanceMode[🔧 Maintenance Mode]
        NotifyDevelopers[👨‍💻 Notify Developers]
        CreateErrorReport[📊 Create Error Report]
    end

    subgraph "Network Error Handling"
        DetectNetworkIssue[🌐 Detect Network Issue]
        ShowOfflineMode[📴 Show Offline Mode]
        QueueOperations[📋 Queue Operations]
        RetryOnConnection[🔄 Retry on Connection]
        CacheFailedRequests[💾 Cache Failed Requests]
    end

    subgraph "Error Recovery"
        AttemptRecovery[🔧 Attempt Recovery]
        RecoverySuccessful{Recovery Success?}
        RestoreOperation[✅ Restore Operation]
        EscalateError[⬆️ Escalate Error]
        ShowFallbackUI[🎯 Show Fallback UI]
    end

    subgraph "User Communication"
        ShowErrorMessage[💬 Show Error Message]
        ProvideContext[📝 Provide Context]
        OfferSolutions[💡 Offer Solutions]
        CollectFeedback[📝 Collect User Feedback]
    end

    subgraph "Error Monitoring"
        LogErrorDetails[📝 Log Error Details]
        UpdateErrorMetrics[📊 Update Error Metrics]
        TriggerAlerts[🚨 Trigger Alerts]
        AnalyzePatterns[📈 Analyze Error Patterns]
    end

    ErrorOccurred --> ClassifyError
    ClassifyError --> ErrorType

    ErrorType --> ValidationError
    ErrorType --> DatabaseError
    ErrorType --> PaymentError
    ErrorType --> AuthenticationError
    ErrorType --> SystemError
    ErrorType --> NetworkError

    ValidationError --> ShowFieldErrors
    ShowFieldErrors --> HighlightInvalidFields
    HighlightInvalidFields --> ProvideCorrection
    ProvideCorrection --> ReturnToForm

    DatabaseError --> LogDatabaseError
    LogDatabaseError --> CheckConnection
    CheckConnection --> RetryOperation
    RetryOperation --> ShowGenericError
    ShowGenericError --> NotifyAdministrator

    PaymentError --> LogPaymentError
    LogPaymentError --> ShowPaymentError
    ShowPaymentError --> OfferRetry
    OfferRetry --> SuggestAlternative
    SuggestAlternative --> ContactSupport

    AuthenticationError --> LogSecurityEvent
    LogSecurityEvent --> ClearSession
    ClearSession --> RedirectToLogin
    RedirectToLogin --> ShowAuthError
    ShowAuthError --> BlockSuspiciousActivity

    SystemError --> LogSystemError
    LogSystemError --> CheckSystemHealth
    CheckSystemHealth --> ShowMaintenanceMode
    ShowMaintenanceMode --> NotifyDevelopers
    NotifyDevelopers --> CreateErrorReport

    NetworkError --> DetectNetworkIssue
    DetectNetworkIssue --> ShowOfflineMode
    ShowOfflineMode --> QueueOperations
    QueueOperations --> RetryOnConnection
    RetryOnConnection --> CacheFailedRequests

    %% All error types lead to recovery attempt
    ReturnToForm --> AttemptRecovery
    NotifyAdministrator --> AttemptRecovery
    ContactSupport --> AttemptRecovery
    BlockSuspiciousActivity --> AttemptRecovery
    CreateErrorReport --> AttemptRecovery
    CacheFailedRequests --> AttemptRecovery

    AttemptRecovery --> RecoverySuccessful
    RecoverySuccessful -->|✅ Success| RestoreOperation
    RecoverySuccessful -->|❌ Failed| EscalateError
    EscalateError --> ShowFallbackUI

    %% User communication for all paths
    RestoreOperation --> ShowErrorMessage
    ShowFallbackUI --> ShowErrorMessage
    ShowErrorMessage --> ProvideContext
    ProvideContext --> OfferSolutions
    OfferSolutions --> CollectFeedback

    %% Error monitoring for all paths
    CollectFeedback --> LogErrorDetails
    LogErrorDetails --> UpdateErrorMetrics
    UpdateErrorMetrics --> TriggerAlerts
    TriggerAlerts --> AnalyzePatterns

    AnalyzePatterns --> End([📊 Error Handled])
```

---

## 🚀 Deployment Architecture

### Cloud Deployment Flow

```mermaid
flowchart TD
    Developer[👨‍💻 Developer]

    subgraph "Development Environment"
        LocalDev[💻 Local Development]
        TestingLocal[🧪 Local Testing]
        CodeReview[👥 Code Review]
        CommitChanges[📝 Commit Changes]
    end

    subgraph "Cloud Development Environment"
        CloudIDE[🌐 Cloud IDE/Editor]
        GitIntegration[🔄 Git Integration]
        EnvironmentSetup[⚙️ Environment Setup]
        DependencyInstall[📦 Dependency Installation]
    end

    subgraph "Application Setup"
        FlaskAppSetup[🎸 Flask App Setup]
        DatabaseSetup[🗄️ Database Setup]
        ChatServiceSetup[💬 Chat Service Setup]
        StaticFilesSetup[📁 Static Files Setup]
    end

    subgraph "Configuration Management"
        SecretsManagement[🔐 Secrets Management]
        EnvironmentVars[🔧 Environment Variables]
        ConfigValidation[✅ Config Validation]
        SecuritySettings[🛡️ Security Settings]
    end

    subgraph "Service Initialization"
        PostgreSQLSetup[🐘 PostgreSQL Setup]
        FlaskServerStart[🎸 Flask Server Start]
        DjangoServiceStart[💬 Django Service Start]
        WebSocketSetup[🔌 WebSocket Setup]
    end

    subgraph "Health Checks"
        DatabaseHealth[💊 Database Health]
        ServiceHealth[💊 Service Health]
        APIHealth[💊 API Health]
        ChatHealth[💊 Chat Health]
    end

    subgraph "Monitoring & Logging"
        ErrorLogging[📝 Error Logging]
        PerformanceMonitoring[📊 Performance Monitoring]
        UserAnalytics[👥 User Analytics]
        SystemMetrics[📈 System Metrics]
    end

    subgraph "Production Features"
        HTTPSEnforcement[🔒 HTTPS Enforcement]
        CORSConfiguration[🌐 CORS Configuration]
        RateLimiting[⏱️ Rate Limiting]
        SecurityHeaders[🛡️ Security Headers]
    end

    Developer --> LocalDev
    LocalDev --> TestingLocal
    TestingLocal --> CodeReview
    CodeReview --> CommitChanges
    CommitChanges --> CloudIDE

    CloudIDE --> GitIntegration
    GitIntegration --> EnvironmentSetup
    EnvironmentSetup --> DependencyInstall

    DependencyInstall --> FlaskAppSetup
    FlaskAppSetup --> DatabaseSetup
    DatabaseSetup --> ChatServiceSetup
    ChatServiceSetup --> StaticFilesSetup

    StaticFilesSetup --> SecretsManagement
    SecretsManagement --> EnvironmentVars
    EnvironmentVars --> ConfigValidation
    ConfigValidation --> SecuritySettings

    SecuritySettings --> PostgreSQLSetup
    PostgreSQLSetup --> FlaskServerStart
    FlaskServerStart --> DjangoServiceStart
    DjangoServiceStart --> WebSocketSetup

    WebSocketSetup --> DatabaseHealth
    DatabaseHealth --> ServiceHealth
    ServiceHealth --> APIHealth
    APIHealth --> ChatHealth

    ChatHealth --> ErrorLogging
    ErrorLogging --> PerformanceMonitoring
    PerformanceMonitoring --> UserAnalytics
    UserAnalytics --> SystemMetrics

    SystemMetrics --> HTTPSEnforcement
    HTTPSEnforcement --> CORSConfiguration
    CORSConfiguration --> RateLimiting
    RateLimiting --> SecurityHeaders

    SecurityHeaders --> ProductionReady[🚀 Production Ready]
    ProductionReady --> End([✅ Deployment Complete])
```

### System Architecture in Production

```mermaid
graph TD
    subgraph "Cloud Platform Infrastructure"
        subgraph "Application Layer"
            FlaskApp[🎸 Flask Application<br/>Port 5000<br/>Main E-commerce App]
            DjangoChat[💬 Django Chat Service<br/>Port 8000<br/>Real-time Chat]
        end

        subgraph "Data Layer"
            PostgresDB[(🐘 PostgreSQL<br/>Main Database<br/>Products, Orders, Users)]
            ChatDB[(💬 SQLite<br/>Chat Database<br/>Messages, Rooms)]
            FileStorage[📁 Static File Storage<br/>Product Images, Documents]
        end

        subgraph "Security Layer"
            HTTPS[🔒 HTTPS Termination]
            CORS[🌐 CORS Headers]
            CSRF[🛡️ CSRF Protection]
            Auth[🔐 JWT Authentication]
        end
    end

    subgraph "External Services"
        StripeAPI[💳 Stripe Payment Gateway]
        MidtransAPI[💰 Midtrans Payment Gateway]
        EmailService[📧 Email Service]
        CourierAPI[🚚 Courier APIs]
    end

    subgraph "Client Applications"
        WebBrowser[🌐 Web Browser<br/>Customer Interface]
        AdminPanel[👨‍💼 Admin Panel<br/>Management Interface]
        MobileView[📱 Mobile View<br/>Responsive Design]
    end

    %% Client connections
    WebBrowser --> HTTPS
    AdminPanel --> HTTPS
    MobileView --> HTTPS

    %% Security layer
    HTTPS --> CORS
    CORS --> CSRF
    CSRF --> Auth

    %% Application connections
    Auth --> FlaskApp
    FlaskApp --> DjangoChat

    %% Data connections
    FlaskApp --> PostgresDB
    FlaskApp --> FileStorage
    DjangoChat --> ChatDB

    %% External service connections
    FlaskApp --> StripeAPI
    FlaskApp --> MidtransAPI
    FlaskApp --> EmailService
    FlaskApp --> CourierAPI

    %% WebSocket connections
    WebBrowser -.->|WebSocket| DjangoChat
    AdminPanel -.->|WebSocket| DjangoChat
    MobileView -.->|WebSocket| DjangoChat
```

---

## 📈 Performance & Scaling Considerations

### Database Performance Optimization

```mermaid
flowchart TD
    DatabaseQuery[🔍 Database Query]

    subgraph "Query Optimization"
        AnalyzeQuery[📊 Analyze Query]
        CheckIndexes[📚 Check Indexes]
        OptimizeJoins[🔗 Optimize Joins]
        QueryCaching[💾 Query Caching]
    end

    subgraph "Connection Management"
        ConnectionPool[🏊 Connection Pool]
        ConnectionLimit[⚖️ Connection Limits]
        ConnectionTimeout[⏰ Connection Timeout]
        HealthCheck[💊 Health Check]
    end

    subgraph "Data Management"
        DataArchiving[📦 Data Archiving]
        IndexMaintenance[🔧 Index Maintenance]
        StatisticsUpdate[📊 Statistics Update]
        VacuumProcess[🧹 Vacuum Process]
    end

    DatabaseQuery --> AnalyzeQuery
    AnalyzeQuery --> CheckIndexes
    CheckIndexes --> OptimizeJoins
    OptimizeJoins --> QueryCaching

    QueryCaching --> ConnectionPool
    ConnectionPool --> ConnectionLimit
    ConnectionLimit --> ConnectionTimeout
    ConnectionTimeout --> HealthCheck

    HealthCheck --> DataArchiving
    DataArchiving --> IndexMaintenance
    IndexMaintenance --> StatisticsUpdate
    StatisticsUpdate --> VacuumProcess

    VacuumProcess --> OptimizedPerformance[⚡ Optimized Performance]
```

### Application Scaling Strategy

```mermaid
flowchart TD
    LoadIncrease[📈 Load Increase]

    subgraph "Horizontal Scaling"
        LoadBalancer[⚖️ Load Balancer]
        MultipleInstances[🔢 Multiple App Instances]
        SessionStickiness[🎯 Session Management]
    end

    subgraph "Vertical Scaling"
        CPUUpgrade[🔧 CPU Upgrade]
        MemoryUpgrade[💾 Memory Upgrade]
        StorageUpgrade[💿 Storage Upgrade]
    end

    subgraph "Caching Strategy"
        ApplicationCache[⚡ Application Cache]
        DatabaseCache[🗄️ Database Cache]
        StaticFileCache[📁 Static File Cache]
        RedisCache[🔴 Redis Cache]
    end

    subgraph "Content Delivery"
        CDN[🌐 Content Delivery Network]
        StaticAssets[📁 Static Assets]
        ImageOptimization[🖼️ Image Optimization]
        Compression[🗜️ Content Compression]
    end

    LoadIncrease --> LoadBalancer
    LoadIncrease --> CPUUpgrade

    LoadBalancer --> MultipleInstances
    MultipleInstances --> SessionStickiness

    CPUUpgrade --> MemoryUpgrade
    MemoryUpgrade --> StorageUpgrade

    SessionStickiness --> ApplicationCache
    StorageUpgrade --> ApplicationCache

    ApplicationCache --> DatabaseCache
    DatabaseCache --> StaticFileCache
    StaticFileCache --> RedisCache

    RedisCache --> CDN
    CDN --> StaticAssets
    StaticAssets --> ImageOptimization
    ImageOptimization --> Compression

    Compression --> ScaledApplication[🚀 Scaled Application]
```

---

## 🎯 Kesimpulan

Dokumentasi flowchart dan diagram ini mencakup:

### ✅ Diagram yang Telah Didokumentasikan:

1. **🏗️ Arsitektur Sistem** - Flask-only dengan Django chat service
2. **🗃️ Entity Relationship Diagram** - Complete database schema
3. **📊 Data Flow Diagram** - Level 0, 1, dan 2 dengan detail
4. **👥 Use Case Diagram** - Semua aktor dan use cases
5. **🛍️ Customer Journey** - Complete customer experience flow
6. **👨‍💼 Admin Workflow** - Dashboard dan management flows
7. **📋 Order Processing** - Complete order lifecycle
8. **💳 Payment Processing** - Multi-gateway payment flow
9. **🔐 Authentication Flow** - Security dan session management
10. **🛒 Cart Management** - Shopping cart operations
11. **📦 Inventory Management** - Stock dan restock flows
12. **💬 Chat System** - Real-time chat architecture
13. **⚠️ Error Handling** - Comprehensive error management
14. **🚀 Deployment Architecture** - Cloud deployment flow

### 🎸 Karakteristik Sistem Hurtrock Music Store:

- **Modern E-commerce Platform** untuk alat musik
- **Flask-only Architecture** dengan Django chat service
- **Multi-payment Gateway** (Stripe & Midtrans)
- **Real-time Chat Support** menggunakan WebSocket
- **Comprehensive Admin Panel** dengan analytics
- **Mobile-responsive Design** dengan theme switching
- **Rock/Metal Themed UI** dengan typography khusus
- **Complete Order Management** dengan shipping labels
- **Inventory Management** dengan stock alerts
- **Security-first Approach** dengan CSRF dan JWT

Dokumentasi ini memberikan panduan lengkap untuk memahami alur kerja, integrasi, dan arsitektur sistem Hurtrock Music Store dari perspektif teknis dan bisnis.

---

**🎸 Hurtrock Music Store** - *Rock Your Music Journey with Modern Technology*

**Made with ❤️ by Fajar Julyana**