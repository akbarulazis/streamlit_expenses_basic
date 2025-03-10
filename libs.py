

class Budgeting():
    def __init__ (self,category):
        self.category = category
        self.budget_set = 0
        self.budget_used = 0
        self.budget_left = 0
        self.set_budget_first_time = False
    def set_budget(self, budget_set):
        self.budget_set = budget_set
        if self.budget_left == 0 and not self.set_budget_first_time:
            self.budget_left = budget_set
            self.set_budget_first_time = True
        return self.budget_set
    def increase_budget_user(self, budget_used):
        if not self.set_budget_first_time:
            print('Set your budget First')
            return 0
        else:
            self.budget_used = budget_used
            self.budget_left = self.budget_left - budget_used
            return self.budget_used 
    def check_budget_left(self):
        if not self.set_budget_first_time:
            print('Set your budget First')
            return 0  
        return self.budget_left
    def delete_category(self,category):
        return category




