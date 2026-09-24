from flask_mail import Message
from backend.app import mail


def send_invoice_email(order):
    """Send the order invoice to the customer's email."""

    customer_email = order.customer.email

    message = Message(
        subject=f"Invoice #{order.invoice_number} - The Cozy Knot",
        sender="YOUR_GMAIL@gmail.com",
        recipients=[customer_email]
    )

    message.html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>The Cozy Knot Invoice</title>
    </head>

    <body style="font-family: Arial, sans-serif;">

        <h2>The Cozy Knot</h2>

        <p>Dear {order.shipping_name},</p>

        <p>
            Thank you for your order!
            Your payment has been successfully confirmed.
        </p>

        <hr>

        <h3>Invoice Details</h3>

        <p>
            <strong>Invoice Number:</strong>
            {order.invoice_number}
        </p>

        <p>
            <strong>Order Number:</strong>
            {order.order_number}
        </p>

        <p>
            <strong>Payment Method:</strong>
            {order.payment_method}
        </p>

        <p>
            <strong>Payment Status:</strong>
            {order.payment_status}
        </p>

        <hr>

        <h3>Shipping Information</h3>

        <p>
            <strong>Name:</strong>
            {order.shipping_name}<br>

            <strong>Phone:</strong>
            {order.shipping_phone}<br>

            <strong>Address:</strong>
            {order.shipping_address}<br>

            <strong>Postal Code:</strong>
            {order.postal_code}
        </p>

        <hr>

        <h3>Order Items</h3>

        <table
            border="1"
            cellpadding="8"
            cellspacing="0"
            style="border-collapse: collapse; width: 100%;"
        >

            <tr>
                <th>Product</th>
                <th>Quantity</th>
                <th>Unit Price</th>
                <th>Total</th>
            </tr>
    """

    for item in order.items:

        message.html += f"""
            <tr>
                <td>{item.product_name}</td>

                <td>
                    {item.quantity}
                </td>

                <td>
                    Rs {item.unit_price}
                </td>

                <td>
                    Rs {item.line_total}
                </td>
            </tr>
        """

    message.html += f"""
        </table>

        <br>

        <h3>Payment Summary</h3>

        <p>
            <strong>Subtotal:</strong>
            Rs {order.subtotal}
            <br>

            <strong>Shipping:</strong>
            Rs {order.shipping_fee}
            <br>

            <strong>Total:</strong>
            Rs {order.total}
        </p>

        <hr>

        <p>
            Thank you for shopping with
            <strong>The Cozy Knot</strong>.
        </p>

        <p>
            This is an automatically generated invoice email.
        </p>

    </body>
    </html>
    """

    mail.send(message)