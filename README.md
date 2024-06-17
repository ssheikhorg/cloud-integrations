# Project Name: AWS CDK IoC with Cognito, iDrive API, and DynamoDB

## Overview

This project demonstrates the implementation of Infrastructure as Code (IoC) using AWS Cloud Development Kit (CDK) in Python. The project integrates AWS Cognito for user authentication, utilizes iDrive APIs to store data in S3 buckets, and employs DynamoDB as the database. The primary objective is to create a scalable and secure cloud infrastructure using AWS services and best practices.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Infrastructure as Code (IoC)**: Utilizes AWS CDK in Python for infrastructure management.
- **User Authentication**: Integrates AWS Cognito for secure user authentication and management.
- **Data Storage**: Uses iDrive APIs to store data in AWS S3 buckets.
- **Database**: Employs DynamoDB for fast and flexible NoSQL database capabilities.

## Architecture

1. **Cognito User Pool**: Manages user authentication and authorization.
2. **S3 Buckets**: Stores data via iDrive APIs.
3. **DynamoDB**: Acts as the primary database for application data.
4. **AWS CDK**: Defines and deploys the entire infrastructure.

## Prerequisites

- AWS Account
- AWS CLI configured
- Node.js (for AWS CDK)
- Python 3.10+ and pip
- AWS CDK Toolkit

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/ssheikhorg/cloud-integrations.git
    cd cloud-integrations
    ```

2. **Install AWS CDK Toolkit**:
    ```sh
    npm install -g aws-cdk
    ```

3. **Create a virtual environment and install dependencies**:
    ```sh
    python3 -m venv .env
    source .env/bin/activate
    pip install -r requirements.txt
    ```

## Usage

1. **Bootstrap your AWS environment**:
    ```sh
    cdk bootstrap
    ```

2. **Deploy the CDK stack**:
    ```sh
    cdk deploy
    ```

3. **Monitor the deployment progress and note down the output values, such as the Cognito User Pool ID, S3 Bucket names, and DynamoDB Table names.**

## Configuration

1. **AWS Cognito**: Configure the Cognito User Pool settings as needed.
2. **iDrive API**: Ensure you have valid iDrive API credentials and configure them in your environment.
3. **DynamoDB**: Set up the required tables and configure the application to use these tables.

### Environment Variables

Use a `src/.env` file in the root directory and replace the missing variables with yours

