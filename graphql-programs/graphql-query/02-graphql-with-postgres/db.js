import postgres from 'postgres'

const sql = postgres(`postgres://postgres:dev@0.0.0.0:5432/postgres?sslmode=disable`, {})

// Create tables once connection is established (if they do not exist)


try {
    await sql`
CREATE TABLE IF NOT EXISTS users(
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL
);`

    await sql`CREATE TABLE IF NOT EXISTS posts(
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE
);`

    await sql`CREATE TABLE IF NOT EXISTS comments(
    id BIGSERIAL PRIMARY KEY,
    body TEXT NOT NULL,
    post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE
);`
} catch (e) {
    console.log('Error while creating tables:', e)
}

export let getUsersCalls = 0
export let getPostsByUserIdCalls = 0
export let getCommentsByPostCalls = 0
export let getUserByIdCalls = 0

export const getUsers = async () => {
    getUsersCalls++
    const users = await sql`SELECT * FROM users;`
    return users
}

export const getPostsByUserId = async (userId) => {
    getPostsByUserIdCalls++
    return await sql`SELECT * FROM posts WHERE user_id = ${userId};`
}

export const getCommentsByPost = async (postId) => {
    getCommentsByPostCalls++
    return await sql`SELECT * FROM comments WHERE post_id = ${postId};`
}

export const getUserById = async (id) => {
    getUserByIdCalls++
    const [u] = await sql`SELECT * FROM users WHERE id = ${id}`
    return u
}

export default sql