class Person {
    private String name;
    public String getName() { return name; }
    public void setName(String newName) { name = newName; }
}
class Student extends Person {
    String grade;
    public void introduce() {
        System.out.println("Hi, I am " + getName() + " and my grade is " + grade);
    }
    public void introduce(String greeting) {
        System.out.println(greeting + "! I am " + getName());
    }
}
public class Main{
    public static void main(String[] args) {
        Student s = new Student();
        s.setName("Aishwarya");
        s.grade = "A";
        s.introduce();
        s.introduce("Good Morning");
    }
}