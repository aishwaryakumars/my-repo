import java.io.*;
public class FileInputDemo {
    public static void main(String[] args) {
        try {
            FileInputStream fileInputStream = new FileInputStream("example.txt");
            int data;
            while ((data = fileInputStream.read()) != -1) {
                System.out.print((char) data);
            }
            fileInputStream.close();
        } catch (IOException e) {
            System.out.println("An error occurred while reading the file: " + e.getMessage());
        }
        try {
            FileOutputStream fileOutputStream = new FileOutputStream("output.txt");  
            String content = "This is an example of writing to a file using FileOutputStream.";
            fileOutputStream.write(content.getBytes()); 
            fileOutputStream.close();
            System.out.println("Data written successfully.");
        } 
        catch ( IOException e) {  
            System.out.println("An error occurred while writing to the file: " + e.getMessage());       
        }
    }
}   