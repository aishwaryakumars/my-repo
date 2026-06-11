import java.util.ArrayList;
import java.util.Scanner;
class Student {
    String sid;
    String name;
    int age;
    String course;
    public Student(String sid, String name, int age, String course) {
        this.sid = sid;
        this.name = name;
        this.age = age;
        this.course = course;
    }
    public void display() {
        System.out.println("\nStudent Details");
        System.out.println("ID: " + sid);
        System.out.println("Name: " + name);
        System.out.println("Age: " + age);
        System.out.println("Course: " + course);
    }
}
public class Main1 {
    public static void main(String[] args) {
        ArrayList<Student> students = new ArrayList<>();
        Scanner scanner = new Scanner(System.in);
        while (true) {
            System.out.println("\n----- Student Management System -----");
            System.out.println("1. Add Student");
            System.out.println("2. View All Students");
            System.out.println("3. Search Student");
            System.out.println("4. Exit");
            System.out.print("Enter your choice: ");
            int choice = scanner.nextInt();
            scanner.nextLine();
            if (choice == 1) {
                System.out.print("Enter Student ID: ");
                String sid = scanner.nextLine();
                System.out.print("Enter Name: ");
                String name = scanner.nextLine();
                System.out.print("Enter Age: ");
                int age = scanner.nextInt();
                scanner.nextLine();
                System.out.print("Enter Course: ");
                String course = scanner.nextLine();
                Student s = new Student(sid, name, age, course);
                students.add(s);
                System.out.println("Student Added Successfully!");
            } else if (choice == 2) {
                if (students.size() == 0) {
                    System.out.println("No Students Found!");
                } else {
                    for (Student student : students) {
                        student.display();
                    }
                }
            } else if (choice == 3) {
                System.out.print("Enter Student ID to Search: ");
                String sid = scanner.nextLine();
                boolean found = false;
                for (Student student : students) {
                    if (student.sid.equals(sid)) {
                        student.display();
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    System.out.println("Student Not Found!");
                }
            } else if (choice == 4) {
                System.out.println("Thank You!");
                break;
            } else {
                System.out.println("Invalid Choice!");
            }
        }
        scanner.close();
    }
}