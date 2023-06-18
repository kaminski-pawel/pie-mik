# Pipeline to etl PIE MIK data

## Project description

The aim of the project is to download the results of business cycle research. The data is published once a month in the form of MIK index (Miesięczny Indeks Koniunktury). The index is a product of cooperation between Polski Instytut Ekonomiczny (PIE) and Bank Gospodarstwa Krajowego (BGK).

## Architecture

// TODO

## How to deploy?

```shell
bash package.sh
cd terraform
terraform apply
```

You will be asked for AWS access key and secret key

## How to test?

```shell
pytest
```
