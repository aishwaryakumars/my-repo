class duck{
    void sound(){
        System.out.println("quack quack");
    }
}
class dog{
    void sound(){
        System.out.println("woof woof");
    }
}
class person{
    void sound(){
        System.out.println("hello");
    }
}
class cat{
    void sound(){
        System.out.println("meow meow");
    }
}
class polymorphism{
    public static void main(String[] args) {
        String name = "John";
        duck d = new duck();
        dog dg = new dog();
        person p = new person();
        cat c = new cat();
        d.sound();
        dg.sound();
        p.sound();
        c.sound();
        System.out.println(name.length());
        System.out.println(new int[]{4, 5, 6}.length);
        System.out.println("A"+"B");
    }
}