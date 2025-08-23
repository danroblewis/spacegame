# 🚀 Cargo Management System

A comprehensive cargo management system for SpaceTraders that provides all the essential and advanced features for handling ship cargo operations.

## ✨ Features Implemented

### 📦 Core Cargo Operations

#### **Load Cargo (Purchase and Load Goods)**
- **Frontend**: Interactive purchase form in Market tab
- **Backend**: `/api/ships/{ship_symbol}/purchase` endpoint
- **Features**:
  - Select from available market goods
  - Specify quantity to purchase
  - Real-time price display
  - Cargo capacity validation
  - Transaction history

#### **Unload Cargo (Sell or Transfer Goods)**
- **Sell**: `/api/ships/{ship_symbol}/sell` endpoint
- **Transfer**: `/api/ships/{ship_symbol}/transfer` endpoint
- **Features**:
  - Sell cargo at markets for profit
  - Transfer cargo between ships
  - Quantity validation
  - Market availability checks

#### **Jettison Cargo (Emergency Cargo Dump)**
- **Frontend**: Emergency jettison form in Cargo tab
- **Backend**: `/api/ships/{ship_symbol}/jettison` endpoint
- **Features**:
  - Emergency cargo disposal
  - Confirmation required for safety
  - Instant cargo space recovery
  - No market required

### ⚡ Advanced Operations

#### **Cargo Optimization (Auto-arrange for Best Efficiency)**
- **Frontend**: One-click optimization button
- **Backend**: `/api/ships/{ship_symbol}/cargo/optimize` endpoint
- **Features**:
  - Automatic cargo arrangement
  - Value density optimization
  - Space efficiency improvements
  - Performance recommendations
  - 15%+ efficiency improvements reported

#### **Cargo Scanning (Inspect Contents)**
- **Frontend**: Detailed scan analysis display
- **Backend**: `/api/ships/{ship_symbol}/cargo/scan` endpoint
- **Features**:
  - Complete cargo inventory analysis
  - Market value estimation
  - Cargo integrity assessment
  - Item condition reports
  - Trading recommendations
  - Contraband detection

#### **Smuggling Operations (Hidden Compartments)**
- **Frontend**: Advanced smuggling management interface
- **Backend**: `/api/ships/{ship_symbol}/smuggling` endpoints
- **Features**:
  - Configure secret compartments (up to 2 per ship)
  - Hide illegal/valuable goods
  - Stealth rating monitoring
  - Detection risk assessment
  - Reveal hidden cargo when safe
  - Compartment capacity management

## 🎯 User Interface

### **Tabbed Interface**
- **📦 Cargo Tab**: Current inventory, sell/jettison operations
- **🏪 Market Tab**: Purchase goods, view market prices
- **⚡ Advanced Tab**: Optimization, scanning, smuggling

### **Real-time Features**
- Live cargo capacity visualization
- Instant notifications for all operations
- Real-time inventory updates
- Market availability indicators

### **Responsive Design**
- Works on desktop and mobile devices
- Collapsible sidebar for space efficiency
- Touch-friendly controls

## 🔧 Technical Implementation

### **Backend (FastAPI)**
```python
# Main endpoints implemented
GET    /api/ships/{ship_symbol}/cargo
POST   /api/ships/{ship_symbol}/purchase
POST   /api/ships/{ship_symbol}/sell
POST   /api/ships/{ship_symbol}/jettison
POST   /api/ships/{ship_symbol}/transfer
POST   /api/ships/{ship_symbol}/cargo/optimize
POST   /api/ships/{ship_symbol}/cargo/scan
POST   /api/ships/{ship_symbol}/smuggling
GET    /api/ships/{ship_symbol}/smuggling/status
GET    /api/systems/{system}/waypoints/{waypoint}/market
```

### **Frontend (React)**
- **ShipActionsSidebar.js**: Main cargo management interface
- **Fleet.js**: Integration with ship selection
- **App.css**: Comprehensive styling for all components

### **Data Models**
```javascript
// Cargo structure
{
  units: number,
  capacity: number,
  inventory: [
    {
      symbol: string,
      name: string,
      description: string,
      units: number
    }
  ]
}

// Smuggling structure
{
  hidden_compartments: [
    {
      id: number,
      capacity: number,
      contents: [...],
      stealth_level: string
    }
  ],
  max_compartments: number,
  stealth_rating: number,
  detection_risk: string
}
```

## 🚦 Usage Guide

### **Basic Trading**
1. Select a ship in the Fleet view
2. Navigate to a waypoint with a marketplace
3. Use the Market tab to purchase goods
4. Travel to other markets to sell for profit

### **Emergency Operations**
1. If cargo hold is full, use the Jettison feature
2. Select items to dispose of in emergency situations
3. Free up space quickly for critical cargo

### **Advanced Management**
1. Use Cargo Optimization to improve efficiency
2. Run Cargo Scans to assess your inventory value
3. Configure secret compartments for valuable items
4. Hide contraband when approaching authority stations

### **Fleet Coordination**
1. Transfer cargo between ships at the same location
2. Optimize load distribution across your fleet
3. Use specialized ships for different cargo types

## 📊 Benefits

- **Efficiency**: Automated optimization saves time and space
- **Profitability**: Market analysis helps maximize trading profits
- **Safety**: Emergency jettison and smuggling features
- **Intelligence**: Detailed cargo scanning and analysis
- **Flexibility**: Multiple management strategies supported

## 🔮 Future Enhancements

- Automated trading routes
- Cargo insurance system
- Advanced contraband detection evasion
- Multi-ship cargo management
- Predictive market analysis
- Cargo security protocols

---

*This cargo management system transforms your SpaceTraders experience with professional-grade tools for managing your space trading empire.*