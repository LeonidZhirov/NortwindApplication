from dataclasses import dataclass

@dataclass
class Customer:
    customer_id: int
    company_name: str
    contact_name: str

    def __str__(self):
        return f"{self.customer_id:<10} | {self.company_name:<40} | {self.contact_name:<30}"