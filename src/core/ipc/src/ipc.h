/*
 * CarrotOS IPC (Inter-Process Communication) Layer
 * ipc.h - Kernel IPC mechanisms
 * 
 * Provides:
 * - Message queues
 * - Shared memory
 * - Semaphores
 * - Sockets
 */

#ifndef __IPC_H__
#define __IPC_H__

#include <stdint.h>
#include <stddef.h>

/* Message queue */
typedef struct {
    uint32_t id;
    uint32_t flags;
    size_t msg_size;
    void *buffer;
} msg_queue_t;

/* Shared memory segment */
typedef struct {
    uint32_t id;
    uint32_t owner_uid;
    size_t size;
    void *address;
    uint16_t permissions;
} shm_segment_t;

/* Semaphore */
typedef struct {
    uint32_t id;
    uint32_t value;
    uint32_t owner_pid;
    int (*wait)(struct ipc_semaphore *sem);
    int (*signal)(struct ipc_semaphore *sem);
} semaphore_t;

/* IPC operations */
int ipc_msgqueue_create(uint32_t key, size_t msg_size);
int ipc_msgqueue_send(int queue_id, const void *msg);
int ipc_msgqueue_recv(int queue_id, void *msg, size_t timeout);

int ipc_shm_create(uint32_t key, size_t size, uint16_t perms);
int ipc_shm_attach(int shm_id, void **address);
int ipc_shm_detach(void *address);

int ipc_sem_create(uint32_t key, uint32_t initial_value);
int ipc_sem_wait(int sem_id);
int ipc_sem_signal(int sem_id);

#endif /* __IPC_H__ */
