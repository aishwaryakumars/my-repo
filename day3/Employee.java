class Employee {
    private String name;
    private int id;
    private double salary;

    public Employee(String name, int id, double salary) {
        this.name = name;
        this.id = id;
        this.salary = salary;
    }

    protected String getName() {
        return name;
    }

    private int getId() {
        return id;
    }

    public double getSalary() {
        return salary;
    }
    public void displayInfo() {
        System.out.println("Employee ID: " + id);
        System.out.println("Employee Name: " + name);
        System.out.println("Employee Salary: $" + salary);
    }
    public static void main(String[] args) {
        Employee emp1 = new Employee("Alice", 101, 50000.0);
        Employee emp2 = new Employee("Bob", 102, 60000.0);

        emp1.displayInfo();
        System.out.println();
        emp2.displayInfo();
    }
}