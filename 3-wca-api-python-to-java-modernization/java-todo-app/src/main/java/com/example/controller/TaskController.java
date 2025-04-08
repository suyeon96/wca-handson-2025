package com.example.controller;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.stream.Collectors;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.model.Task;

@RestController
@RequestMapping("/tasks")
@CrossOrigin
public class TaskController {

    private static final String TASKS_FILE = "tasks.json";

    @GetMapping
    public ResponseEntity<List<Task>> getTasks() throws IOException {
        String json = Files.readString(getPath());
        return ResponseEntity.ok(List.of(json.split(",")).stream().map(Task::new).collect(Collectors.toList()));
    }

    @PostMapping
    public ResponseEntity<String> addTask(@RequestBody Task task) throws IOException {
        String tasks = Files.readString(getPath());
        tasks += "," + task.getName();
        Files.writeString(getPath(), tasks);
        return ResponseEntity.status(HttpStatus.CREATED).body("Task added successfully");
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<String> deleteTask(@PathVariable("id") int id) throws IOException {
        return ResponseEntity.ok("Task deleted successfully");
    }

    @PutMapping("/{id}")
    public ResponseEntity<String> updateTask(@PathVariable("id") int id, @RequestBody Task task) throws IOException {
        return ResponseEntity.ok("Task updated successfully");
    }

    private Path getPath() {
        return Paths.get(TASKS_FILE);
    }

}
