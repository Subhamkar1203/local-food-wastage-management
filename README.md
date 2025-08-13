


# Local Food Wastage Management System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-orange)](https://streamlit.io/)

A data-driven application that connects surplus food providers with those in need. Built with **Streamlit**, this platform provides an intuitive interface for managing food listings, tracking claims, and analyzing data to reduce food waste and promote social good.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Technologies Used](#technologies-used)
- [Data Model](#data-model)
- [Setup and Installation](#setup-and-installation)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Screenshots](#screenshots)

---

## Project Overview
Food wastage is a major global problem. This project addresses it by creating a structured platform for redistribution, making it easier for restaurants, supermarkets, and individuals to donate surplus food and for shelters, charities, and individuals to receive it.

---

## Key Features
- **Food Listings Management**: Interactive interface to display, filter, and manage available food items.
- **CRUD Operations**: Create, Read, Update, and Delete food listings.
- **Data Analysis Dashboard**: Visualizations and metrics to identify trends in food donation, claims, and wastage.
- **Database Integration**: SQL database to store and manage provider, receiver, food, and claim information.
- **Accessibility**: User-friendly, responsive web application built with Streamlit.

---

## Technologies Used
- **Python** – Core programming language for application logic.
- **Streamlit** – Framework for creating interactive web applications.
- **Pandas** – Data manipulation and analysis library.
- **SQLite3** – Lightweight SQL database for storage.
- **Git & GitHub** – Version control and code hosting.

---

## Data Model
The application uses CSV files as data sources, representing a simple relational database model:

| File | Description |
|------|-------------|
| `food_listings_data.csv` | Details about food items available for donation. |
| `claims_data.csv` | Records of food items claimed by receivers. |
| `providers_data.csv` | Information about food donors (restaurants, supermarkets, etc.). |
| `receivers_data.csv` | Information about food receivers (NGOs, individuals, etc.). |

---

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/Subhamkar1203/local-food-wastage-management.git
cd local-food-wastage-management
````


### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the Application

```bash
streamlit run app.py
```

The app will open in your default web browser at [http://localhost:8501](http://localhost:8501).

---

## Deployment

The application can be deployed on cloud platforms like **Streamlit Community Cloud** or **Hugging Face Spaces**. Simply connect your GitHub repository to the platform and follow the deployment instructions.

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes and commit them: `git commit -m "Add feature"`.
4. Push to the branch: `git push origin feature-name`.
5. Open a Pull Request.

---
