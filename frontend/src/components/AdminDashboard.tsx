import { Button, Card, Select, Table, Text } from "@mantine/core";
import { useListState } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import {
	deleteUser as deleteUserOnBackend,
	getUsers,
	updateUser as updateUserOnBackend,
} from "auth";
import { getEnumKeys } from "helpers";
import { BackendAuthLevel, BackendUser } from "interfaces";
import { useEffect } from "react";

export default function AdminDashboard() {
	const [users, usersHandler] = useListState<BackendUser>(undefined);

	useEffect(() => {
		getUsers().then((res) => {
			usersHandler.setState(res);
		});
	}, []);

	const updateUsers = (user: BackendUser) => {
		usersHandler.setItem(
			users.findIndex((u) => u.email === user.email),
			user,
		);
	};

	const deleteUser = (user: BackendUser) => {
		deleteUserOnBackend(user).then((res) => {
			if (res.status === 200) {
				notifications.show({
					title: "Success",
					message: "User deleted.",
					autoClose: 1000,
				});
				usersHandler.remove(users.findIndex((u) => u.email === user.email));
			}
		});
	};

	if (!users) {
		return <>Loading...</>;
	} else {
		return (
			<div
				style={{
					display: "flex",
					justifyContent: "center",
				}}
			>
				<Card mt={20} shadow="xs" padding="md" withBorder pos={"relative"}>
					<Text size="xl">Unauthorized users</Text>
					<Card.Section inheritPadding>
						<UserTable
							users={users.filter(
								(user) => user.auth_level === BackendAuthLevel.UNAUTHORIZED,
							)}
							updateUsers={updateUsers}
							deleteUser={deleteUser}
						/>
					</Card.Section>
					<Text size="xl">Authorized users</Text>
					<Card.Section inheritPadding>
						<UserTable
							users={users.filter(
								(user) => user.auth_level !== BackendAuthLevel.UNAUTHORIZED,
							)}
							updateUsers={updateUsers}
							deleteUser={deleteUser}
						/>
					</Card.Section>
				</Card>
			</div>
		);
	}
}

function UserTable({
	users,
	updateUsers,
	deleteUser,
}: {
	users: BackendUser[];
	updateUsers: (user: BackendUser) => void;
	deleteUser: (user: BackendUser) => void;
}) {
	const setAuthLevel = (user: BackendUser, newAuthLevel: string | null) => {
		if (newAuthLevel === null) {
			return;
		}

		const updatedUser = { ...user };
		updatedUser.auth_level =
			BackendAuthLevel[newAuthLevel as keyof typeof BackendAuthLevel];
		updateUserOnBackend(updatedUser).then((res) => {
			if (res.status === 200) {
				notifications.show({
					title: "Success",
					message: "User updated.",
					autoClose: 1000,
				});
				updateUsers(updatedUser);
			}
		});
	};

	return (
		<Table>
			<Table.Thead>
				<Table.Tr>
					<Table.Th>Email</Table.Th>
					<Table.Th>Authorization level</Table.Th>
					<Table.Th> </Table.Th>
				</Table.Tr>
			</Table.Thead>
			<Table.Tbody>
				{users.map((user) => (
					<Table.Tr key={user.email}>
						<Table.Td>{user.email}</Table.Td>
						<Table.Td>
							<Select
								data={getEnumKeys(BackendAuthLevel)}
								defaultValue={BackendAuthLevel[user.auth_level]}
								onChange={(value) => setAuthLevel(user, value)}
							/>
						</Table.Td>
						<Table.Td>
							<Button color="red" onClick={() => deleteUser(user)}>
								Delete
							</Button>
						</Table.Td>
					</Table.Tr>
				))}
			</Table.Tbody>
		</Table>
	);
}
