from pydantic import BaseModel, Field
from typing import List, Optional

class InvoiceItem(BaseModel):
    description: str = Field(description="Description of the item or service.")
    amount: float = Field(description="The cost or amount for this item. Do not include currency symbols, just the number.")

class InvoiceModel(BaseModel):
    invoice_number: str = Field(description="The unique invoice number.")
    date: str = Field(description="The date of the invoice.")
    bill_to: str = Field(description="The name of the company or person being billed.")
    items: List[InvoiceItem] = Field(description="The list of line items in the invoice.")
    subtotal: float = Field(description="The subtotal before taxes.")
    tax_amount: float = Field(description="The tax amount.")
    total: float = Field(description="The final total amount.")
