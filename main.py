from libs import Budgeting
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


def load_categories_csv():
    try:
        categories = pd.read_csv('categories.csv')
        all_categories = {}
        for _, row in categories.iterrows():
            categories_name = row['category']
            categories_class = Budgeting(categories_name)
            categories_class.budget_set = row['budget_set']
            categories_class.budget_used = row['budget_used']
            categories_class.budget_left = row['budget_left']
            categories_class.set_budget_first_time = row['set_budget_first_time']
            all_categories[categories_name] = categories_class
        return all_categories
    except FileNotFoundError:
        return {}

def load_expenses_csv():
    try:
        expenses = pd.read_csv('expenses.csv')
        return expenses.to_dict('records')
    except FileNotFoundError:
        return []
    

def save_categories_to_csv():
    categories_data = []
    for cat_name, cat_obj in st.session_state.categories.items():
        categories_data.append({
            "category": cat_name,
            "budget_set": cat_obj.budget_set,
            "budget_used": cat_obj.budget_used,
            "budget_left": cat_obj.budget_left,
            "set_budget_first_time": cat_obj.set_budget_first_time
        })
    

    pd.DataFrame(categories_data).to_csv("categories.csv", index=False)

def save_expenses_to_csv():
    pd.DataFrame(st.session_state.expenses).to_csv("expenses.csv", index=False)


if "categories" not in st.session_state:
    st.session_state.categories = load_categories_csv()

if "expenses" not in st.session_state:
    st.session_state.expenses = load_expenses_csv()

st.title('Budget Management System')

page = st.sidebar.selectbox("Menu",['Dashboard', 'Input Expenses', 'Create Category and Budget','Delete Category and Budget'])

if page == 'Dashboard':
    st.header('Budget Dashboard')

    total_budget = sum([categories.budget_set for categories in st.session_state.categories.values()])
    total_used = sum([categories.budget_used for categories in st.session_state.categories.values()]) 
    total_left = sum([categories.budget_left for categories in st.session_state.categories.values()])    

    col1, col2, col3 = st.columns(3)

    col1.metric('Total Budget', f"Rp {int(total_budget):,}")
    col2.metric('Total Used', f"Rp {int(total_used):,}")
    col3.metric('Total Remaining', f"Rp {int(total_left):,}")

    if st.session_state.categories:
        st.subheader("Budget Usage by Category")
        chart_data = pd.read_csv('categories.csv')
        chart_data.rename(columns={"category": "Category", "budget_used": "Budget Used", "budget_left": "Budget Remaining"}, inplace=True)
        chart_fig = pd.melt(chart_data, 
                                    id_vars=['Category'], 
                                    value_vars=['Budget Used', 'Budget Remaining'],
                                    var_name='Status', value_name='Amount')
        
        bar_chart = px.bar(chart_fig, x='Category', y='Amount', color='Status',
                        title='Budget Status by Category',
                        barmode='stack')
        st.plotly_chart(bar_chart)

    if st.session_state.expenses:
        st.subheader("Recent Expenses")
        expense = pd.DataFrame(st.session_state.expenses)
        st.dataframe(expense)
    else:
        st.info("No expenses recorded yet.")

elif page == "Input Expenses":
    st.header("Insert New Expenses")
    
    if not st.session_state.categories:
        st.warning("Create Category!")
    else:
       
        expense_name = st.text_input("Expense Name")
        
    
        valid_categories = [categories for categories, object in st.session_state.categories.items() 
                           if object.set_budget_first_time]
        
        if not valid_categories:
            st.warning("Set Budget dulu!")
        else:
            category = st.selectbox("Category", valid_categories)
            amount = st.number_input("Amount (Rp)", min_value=100, step=1000)
            
            if st.button("Add Expense"):
                if amount <= 0:
                    st.error("Tidak boleh kurang dari 0")
                elif not expense_name:
                    st.error("Masukan nama pengeluaran")
                else:
                
                    categories_class = st.session_state.categories[category]
                    
                    if amount > categories_class.budget_left:
                        st.error(f"Lebih dari budget {category}! Budget sisa Rp {int(categories_class.budget_left):,} Tersisa.")
                    else:
                        categories_class.increase_budget_user(amount)
        
                        st.session_state.expenses.append({
                            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Name": expense_name,
                            "Category": category,
                            "Amount": amount
                        })
                        
                        st.success(f"Added expense: {expense_name} Rp{int(amount):,} to {category}")
                        st.info(f"Remaining budget for {category}: Rp{int(categories_class.budget_left):,}")
                        
                      
                        save_expenses_to_csv()
                        save_categories_to_csv()


elif page == "Create Category and Budget":
    st.header("Create Category and Set Budget")
    

    if st.session_state.categories:
        st.subheader("Existing Categories")
        for name_categories, categories_object in st.session_state.categories.items():
            st.write(f"**{name_categories}**: Budget: Rp {int(categories_object.budget_set):,}, Used: Rp {int(categories_object.budget_used):,}, Remaining: Rp {int(categories_object.budget_left):,}")
    

    st.subheader("Add New Category")
    new_category = st.text_input("Category Name")
    budget_amount = st.number_input("Budget Amount (Rp)", min_value=100, step=10_000)
    
    if st.button("Create Category and Set Budget"):
        if not new_category:
            st.error("Please enter valid name.")
        elif budget_amount <= 0:
            st.error("Please enter valid amount.")
        elif new_category in st.session_state.categories:
            st.error(f"Category '{new_category}' already exists!")
        else:
         
            categories_class = Budgeting(new_category)
            categories_class.set_budget(budget_amount)
            st.session_state.categories[new_category] = categories_class

            save_categories_to_csv()
            
            st.success(f"Created category '{new_category}' with budget Rp {int(budget_amount):,}")
    
elif page == "Delete Category and Budget":
    st.header("Delete Category")
    
    if not st.session_state.categories:
        st.warning("No categories to delete.")
    else:
        st.subheader("Category List")

        categories_data = []
        for categories_name, categories_object in st.session_state.categories.items():
            categories_data.append({
                "Category": categories_name,
                "Budget": f"Rp {int(categories_object.budget_set) :,}",
                "Used": f"Rp {int(categories_object.budget_used):,}",
                "Remaining": f"Rp {int(categories_object.budget_left):,}"
            })
        
        df = pd.DataFrame(categories_data)
        st.dataframe(df)
   
        delete_category = st.selectbox("Select Category to Delete", list(st.session_state.categories.keys()))
        
        if delete_category:
            cat_expenses = [exp for exp in st.session_state.expenses if exp["Category"] == delete_category]
            st.warning(f"This category has {len(cat_expenses)} expenses recorded. Deleting will remove these expense records.")
        if st.button("Delete Category"):
            

            st.session_state.expenses = [exp for exp in st.session_state.expenses if exp["Category"] != delete_category]
  
            del st.session_state.categories[delete_category]
            
     
            save_categories_to_csv()
            save_expenses_to_csv()
            
            st.success(f"Deleted category '{delete_category}' and its expense records.")
            st.rerun()
