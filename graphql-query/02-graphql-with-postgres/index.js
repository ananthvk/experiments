// A simple graphql server example for a blog site with users, posts and comments
// users(id, name)
// posts(id, title, body, user_id)
// comments(id, body, post_id, user_id)

// TOOD: For now only query will be implemented, mutations will be implemented later

// Program to demonstrate N+1 explosion when using GraphQL in a naive way

// The goal of this small application is to find out how many SQL queries is executed, and the possible attacks on it

import { graphql, GraphQLID, GraphQLList, GraphQLNonNull, GraphQLObjectType, GraphQLSchema, GraphQLString } from "graphql";
import express from 'express'
import sql, { getCommentsByPost, getCommentsByPostCalls, getPostsByUserId, getPostsByUserIdCalls, getUserById, getUserByIdCalls, getUsers, getUsersCalls } from "./db.js";
import { createHandler } from 'graphql-http/lib/use/express';
import { ruruHTML } from "ruru/server";

console.log('connected to database')

// GraphQL schemas and types
let resolveCallCounts = {
    users: 0,
    posts: 0,
    postAuthor: 0,
    postComments: 0,
    commentAuthor: 0
};

const UserType = new GraphQLObjectType({
    name: 'User',
    fields: () => ({
        id: { type: new GraphQLNonNull(GraphQLID) },
        name: { type: new GraphQLNonNull(GraphQLString) },
        posts: {
            type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(PostType))),
            resolve: (user) => {
                resolveCallCounts.posts++;
                console.log('resolving posts for user', user.id, '(', user.name, ')')
                return getPostsByUserId(user.id)
            }
        }
    })
})

const PostType = new GraphQLObjectType({
    name: 'Post',
    fields: () => ({
        id: { type: new GraphQLNonNull(GraphQLID) },
        title: { type: new GraphQLNonNull(GraphQLString) },
        body: { type: new GraphQLNonNull(GraphQLString) },
        author: {
            type: new GraphQLNonNull(UserType),
            resolve: (post) => {
                resolveCallCounts.postAuthor++;
                console.log('resolving author for post', post.id)
                return getUserById(post.user_id)
            }
        },
        comments: {
            type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(CommentType))),
            resolve: (post) => {
                resolveCallCounts.postComments++;
                console.log('resolving comments for post', post.id)
                return getCommentsByPost(post.id)
            }
        }
    })
})

const CommentType = new GraphQLObjectType({
    name: 'Comment',
    fields: {
        id: { type: new GraphQLNonNull(GraphQLID) },
        body: { type: new GraphQLNonNull(GraphQLString) },
        author: {
            type: new GraphQLNonNull(UserType),
            resolve: (comment) => {
                resolveCallCounts.commentAuthor++;
                console.log('resolving author for comment', comment.id)
                return getUserById(comment.user_id)
            }
        }
    }
})

const schema = new GraphQLSchema({
    query: new GraphQLObjectType({
        name: 'Query',
        fields: {
            users: {
                type: new GraphQLNonNull(new GraphQLList(UserType)),
                resolve: async () => {
                    resolveCallCounts.users++;
                    console.log('resolving all users')
                    return getUsers()
                }
            }
        }
    })
});

// Middlewares

const loggingMiddleware = (req, res, next) => {
    const start = Date.now();
    console.log('Start profiling....')

    const currentGetUsers = getUsersCalls
    const currentGetPosts = getPostsByUserIdCalls
    const currentGetComments = getCommentsByPostCalls
    const currentGetUser = getUserByIdCalls
    const currentResolveCounts = { ...resolveCallCounts }

    res.on('finish', () => {
        const duration = Date.now() - start;
        const queryCounts = {
            users: getUsersCalls - currentGetUsers,
            posts: getPostsByUserIdCalls - currentGetPosts,
            comments: getCommentsByPostCalls - currentGetComments,
            user: getUserByIdCalls - currentGetUser
        };
        
        const resolveCounts = {
            users: resolveCallCounts.users - currentResolveCounts.users,
            posts: resolveCallCounts.posts - currentResolveCounts.posts,
            postAuthor: resolveCallCounts.postAuthor - currentResolveCounts.postAuthor,
            postComments: resolveCallCounts.postComments - currentResolveCounts.postComments,
            commentAuthor: resolveCallCounts.commentAuthor - currentResolveCounts.commentAuthor
        };
        
        const total = queryCounts.users + queryCounts.posts + queryCounts.comments + queryCounts.user
        const totalResolves = resolveCounts.users + resolveCounts.posts + resolveCounts.postAuthor + resolveCounts.postComments + resolveCounts.commentAuthor

        console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} - IP: ${req.ip} - Status: ${res.statusCode} - ${duration}ms`);
        console.log(`SQL Queries - Users: ${queryCounts.users}, Posts: ${queryCounts.posts}, Comments: ${queryCounts.comments}, User: ${queryCounts.user}, Total: ${total}`);
        console.log(`Resolve calls - Users: ${resolveCounts.users}, Posts: ${resolveCounts.posts}, PostAuthor: ${resolveCounts.postAuthor}, PostComments: ${resolveCounts.postComments}, CommentAuthor: ${resolveCounts.commentAuthor}, Total: ${totalResolves}`); 
    });
    next();
};

// Create express app

const app = express();
app.use(loggingMiddleware)

app.all(
    '/graphql',
    createHandler({
        schema: schema
    })
)

app.get('/', (_req, res) => {
    res.type('html');
    res.end(ruruHTML({ endpoint: '/graphql' }));
});

app.listen(5000)
console.log("Running GraphQL server at http://localhost:5000/graphql")

/* Example
{
  users {
    ...getPosts
  }
}

fragment getPosts on User{
  name
  id
  posts {
    title
    author {
      name
    }
    comments {
      body
      author {
        name
      }
    }
}
}
*/