# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db

class PayTable(db.Model):
    __tablename__ = 'pay_table'

    id = db.Column(db.Integer, primary_key=True)
    pay_order_id = db.Column(db.Integer, nullable=False, unique=True, server_default=db.FetchedValue())
    table_name = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue())
    table_volume = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    table_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
