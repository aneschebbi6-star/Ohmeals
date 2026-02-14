"""
Accounting service layer for OHMEALS.
All financial queries use DB-level aggregation for performance.
"""
from datetime import date, datetime, timedelta
from sqlalchemy import func, cast, Date

from app.extensions import db
from app.models.order import Order
from app.models.expense import Expense


# Status that counts as "paid" revenue
PAID_STATUS = 'Livrée'


def get_revenue(start_date, end_date):
    """Get total revenue from delivered orders in date range."""
    result = db.session.query(
        func.coalesce(func.sum(Order.total_price), 0)
    ).filter(
        Order.status == PAID_STATUS,
        cast(Order.created_at, Date) >= start_date,
        cast(Order.created_at, Date) <= end_date
    ).scalar()
    return float(result)


def get_total_expenses(start_date, end_date):
    """Get total expenses in date range."""
    result = db.session.query(
        func.coalesce(func.sum(Expense.amount), 0)
    ).filter(
        Expense.date >= start_date,
        Expense.date <= end_date
    ).scalar()
    return float(result)


def get_profit(start_date, end_date):
    """Calculate net profit = revenue - expenses."""
    revenue = get_revenue(start_date, end_date)
    expenses = get_total_expenses(start_date, end_date)
    return revenue - expenses


def get_financial_summary(period='month'):
    """
    Get financial summary for a given period.
    period: 'today', 'week', 'month'
    Returns: dict with revenue, expenses, profit, margin
    """
    today = date.today()

    if period == 'today':
        start_date = today
        end_date = today
    elif period == 'week':
        start_date = today - timedelta(days=today.weekday())  # Monday
        end_date = today
    else:  # month
        start_date = today.replace(day=1)
        end_date = today

    revenue = get_revenue(start_date, end_date)
    expenses = get_total_expenses(start_date, end_date)
    profit = revenue - expenses
    margin = (profit / revenue * 100) if revenue > 0 else 0

    return {
        'period': period,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'revenue': round(revenue, 2),
        'expenses': round(expenses, 2),
        'profit': round(profit, 2),
        'margin': round(margin, 1)
    }


def get_revenue_chart_data(start_date, end_date, granularity='daily'):
    """
    Get revenue data grouped by date for line chart.
    granularity: 'daily', 'weekly', 'monthly'
    """
    if granularity == 'monthly':
        # Group by year-month
        date_label = func.strftime('%Y-%m', Order.created_at)
    elif granularity == 'weekly':
        # Group by year-week
        date_label = func.strftime('%Y-W%W', Order.created_at)
    else:
        # Group by day
        date_label = func.strftime('%Y-%m-%d', Order.created_at)

    results = db.session.query(
        date_label.label('label'),
        func.coalesce(func.sum(Order.total_price), 0).label('total')
    ).filter(
        Order.status == PAID_STATUS,
        cast(Order.created_at, Date) >= start_date,
        cast(Order.created_at, Date) <= end_date
    ).group_by(date_label).order_by(date_label).all()

    return [{'label': r.label, 'total': round(float(r.total), 2)} for r in results]


def get_expenses_by_category(start_date, end_date):
    """Get expenses grouped by category for pie chart."""
    results = db.session.query(
        Expense.category,
        func.coalesce(func.sum(Expense.amount), 0).label('total')
    ).filter(
        Expense.date >= start_date,
        Expense.date <= end_date
    ).group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).all()

    return [{'category': r.category, 'total': round(float(r.total), 2)} for r in results]


def get_expenses_list(start_date=None, end_date=None, page=1, per_page=20):
    """Get paginated list of expenses with optional date filter."""
    query = Expense.query

    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)

    query = query.order_by(Expense.date.desc())

    # Paginate
    total = query.count()
    expenses = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        'expenses': [e.to_dict() for e in expenses],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }


def get_export_data(start_date, end_date):
    """Get all financial data for CSV export."""
    # Revenue entries (delivered orders)
    orders = Order.query.filter(
        Order.status == PAID_STATUS,
        cast(Order.created_at, Date) >= start_date,
        cast(Order.created_at, Date) <= end_date
    ).order_by(Order.created_at).all()

    # Expense entries
    expenses = Expense.query.filter(
        Expense.date >= start_date,
        Expense.date <= end_date
    ).order_by(Expense.date).all()

    revenue_rows = []
    for o in orders:
        revenue_rows.append({
            'type': 'Revenu',
            'date': o.created_at.strftime('%Y-%m-%d') if o.created_at else '',
            'description': f'Commande #{o.id} - {o.customer_name}',
            'category': 'Vente',
            'amount': float(o.total_price)
        })

    expense_rows = []
    for e in expenses:
        expense_rows.append({
            'type': 'Dépense',
            'date': e.date.isoformat(),
            'description': e.title,
            'category': e.category,
            'amount': -float(e.amount)  # Negative for expenses
        })

    return revenue_rows + expense_rows
