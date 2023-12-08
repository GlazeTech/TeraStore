// auth-service.test.ts
import { deleteUser, getUsers, register, updateUser } from "auth/auth-service";
import { BackendAuthLevel } from "interfaces";

import { describe, expect, test } from "vitest";

describe("register", () => {
	test("should register a new user", async () => {
		const email = "test@example.com";
		const password = "password123";
		const response = await register(email, password);
		expect(response.status).toBe(200);
	});
	test("should create, verify, and delete a user", async () => {
		const email = "test2@example.com";
		const password = "password123";

		// Create a new user
		const registerResponse = await register(email, password);
		expect(registerResponse.status).toBe(200);

		// List all users and verify the new user exists
		const users = await getUsers();
		const newUser = users.find((user) => user.email === email);
		if (!newUser) {
			throw new Error("New user not found");
		}
		expect(newUser).toBeDefined();

		// Delete the new user

		const deleteResponse = await deleteUser(newUser);
		expect(deleteResponse.status).toBe(200);

		// List all users and verify the new user has been deleted
		const updatedUsers = await getUsers();
		const deletedUser = updatedUsers.find((user) => user.email === email);
		expect(deletedUser).toBeUndefined();
	});
	test("should create a user and update the user role", async () => {
		const email = "test3@example.com";
		const password = "password123";
		const newRole = BackendAuthLevel.USER;

		// Create a new user
		const registerResponse = await register(email, password);
		expect(registerResponse.status).toBe(200);

		// List all users and find the new user
		const users = await getUsers();
		const newUser = users.find((user) => user.email === email);
		if (!newUser) {
			throw new Error("New user not found");
		}
		expect(newUser).toBeDefined();

		// Update the new user's role
		const updateResponse = await updateUser({
			...newUser,
			auth_level: newRole,
		});
		expect(updateResponse.status).toBe(200);

		// List all users and verify the new user's role has been updated
		const updatedUsers = await getUsers();
		const updatedUser = updatedUsers.find((user) => user.email === email);
		if (!updatedUser) {
			throw new Error("Updated user not found");
		}
		expect(updatedUser.auth_level).toBe(newRole);
	});
});
