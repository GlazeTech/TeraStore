import {
	Button,
	Card,
	Divider,
	Group,
	Modal,
	Select,
	Table,
	Text,
	TextInput,
} from "@mantine/core";
import { useDisclosure, useListState } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { addDevice, getDevices } from "api";
import {
	deleteUser as deleteUserOnBackend,
	getUsers,
	updateUser as updateUserOnBackend,
} from "auth";
import { getEnumKeys } from "helpers";
import { BackendAuthLevel, BackendTHzDevice, BackendUser } from "interfaces";
import { useEffect, useState } from "react";
import Header from "./Header";

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
		const isConfirmed = window.confirm(
			"Are you sure you want to delete this user?",
		);
		if (!isConfirmed) {
			return;
		}
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
			<>
				<Header />
				<Divider m={5} />
				<div
					style={{
						display: "flex",
						justifyContent: "center",
					}}
				>
					<Group justify="space-between">
						<DevicesCard />
						<UsersCard
							users={users}
							updateUsers={updateUsers}
							deleteUser={deleteUser}
						/>
					</Group>
				</div>
			</>
		);
	}
}

function UsersCard({
	users,
	updateUsers,
	deleteUser,
}: {
	users: BackendUser[];
	updateUsers: (user: BackendUser) => void;
	deleteUser: (user: BackendUser) => void;
}) {
	return (
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
	);
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

function DevicesCard() {
	const [modalIsOpen, modalHandler] = useDisclosure(false);
	const [newSerialNumberValue, setNewSerialNumberValue] = useState("");
	const [devices, devicesHandler] = useListState<BackendTHzDevice>(undefined);

	useEffect(() => {
		getDevices().then((res) => {
			devicesHandler.setState(res);
		});
	}, []);

	const addDeviceOnBackend = (deviceSerialNumber: string) => {
		addDevice(deviceSerialNumber)
			.then(() => {
				notifications.show({
					title: "Success",
					message: "Device added.",
					autoClose: 2000,
				});
				modalHandler.toggle();
				devicesHandler.append({ serial_number: deviceSerialNumber });
			})
			.catch((err) => {
				notifications.show({
					title: "Error",
					message: err.response.data.detail,
					autoClose: 4000,
					color: "red",
				});
			});
	};
	return (
		<Card mt={20} shadow="xs" padding="md" withBorder pos={"relative"}>
			<Modal
				opened={modalIsOpen}
				onClose={modalHandler.close}
				title={"Add device"}
			>
				<TextInput
					label="Serial number"
					placeholder="Serial number"
					onChange={(event) =>
						setNewSerialNumberValue(event.currentTarget.value)
					}
				/>
				<Button
					color="blue"
					onClick={() => addDeviceOnBackend(newSerialNumberValue)}
				>
					Add
				</Button>
			</Modal>
			<Group justify="space-between">
				<Text size="xl">Devices</Text>
				<Button color="blue" onClick={modalHandler.toggle}>
					Add device
				</Button>
			</Group>
			<Card.Section inheritPadding>
				<DeviceTable devices={devices} />
			</Card.Section>
		</Card>
	);
}

function DeviceTable({
	devices,
}: {
	devices: BackendTHzDevice[];
}) {
	return (
		<Table>
			<Table.Thead>
				<Table.Tr>
					<Table.Th>Serial number</Table.Th>
					<Table.Th> </Table.Th>
				</Table.Tr>
			</Table.Thead>
			<Table.Tbody>
				{devices.map((device) => (
					<Table.Tr key={device.serial_number}>
						<Table.Td>{device.serial_number}</Table.Td>
						<Table.Td>
							<Button size="xs" color="blue">
								Attributes
							</Button>
						</Table.Td>
						<Table.Td>
							<Button size="xs" color="blue">
								Update
							</Button>
						</Table.Td>
					</Table.Tr>
				))}
			</Table.Tbody>
		</Table>
	);
}
