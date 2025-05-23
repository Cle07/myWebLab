// rustimport:pyo3

//:
//: [dependencies]
//: rust-fuzzy-search = "0.1.1"

use pyo3::prelude::*;
use rust_fuzzy_search::fuzzy_search_best_n;
use std::fs::{File, ReadDir};

#[pyfunction]
fn fuzzy_search(query: &str, command: bool, authenticated: bool) -> Vec<String> {
    // This function will implement a fuzzy search for articles
    match command {
        true => {
            let possible_commands = if authenticated {
                vec!["logout".to_string()]
            } else {
                vec!["login".to_string()]
            };
            possible_commands
                .into_iter()
                .filter(|command| command.contains(query))
                .collect()
        }
        false => {
            let mut articles = Vec::new();
            let dir: ReadDir = std::fs::read_dir("articles").unwrap();

            for entry in dir {
                let entry = entry.unwrap();
                if entry
                    .path()
                    .extension()
                    .map(|ext| ext == "md")
                    .unwrap_or(false)
                {
                    articles.push(entry.file_name().to_string_lossy().into_owned());
                }
            }
            let articles_content: Vec<String> = articles
                .iter()
                .map(|article| std::fs::read_to_string(format!("articles/{}", article)).unwrap())
                .collect();

            let articles_content_refs: Vec<&str> =
                articles_content.iter().map(|s| s.as_str()).collect();
            let results = fuzzy_search_best_n(query, &articles_content_refs, 5);
            results
                .into_iter()
                .map(|(matched_content, _score)| {
                    // Find the index of the matched content in articles_content
                    let idx = articles_content
                        .iter()
                        .position(|content| content == matched_content)
                        .unwrap();
                    articles[idx].clone()
                })
                .collect()
        }
    }
}
