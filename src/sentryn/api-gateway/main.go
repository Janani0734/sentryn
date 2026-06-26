package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"regexp"

	"github.com/gofiber/fiber/v2"
)

var credentialRegex = regexp.MustCompile(`(?i)(password|secret|passwd|db_url|api_key)\s*=\s*[^\s]+`)

func main() {
	app := fiber.New()

	app.Post("/gateway/inspect", func(c *fiber.Ctx) error {
		rawBody := c.Body()
		scrubbedBody := credentialRegex.ReplaceAllString(
			string(rawBody), "$1=[REDACTED_BY_SENTRYN]",
		)

		resp, err := http.Post(
			"http://localhost:8000/evaluate",
			"application/json",
			bytes.NewBuffer([]byte(scrubbedBody)),
		)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{
				"error": "Oversight engine disconnected",
			})
		}
		defer resp.Body.Close()

		var evaluationResult map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&evaluationResult)

		if resp.StatusCode == 423 {
			return c.Status(423).JSON(evaluationResult)
		}

		return c.Status(200).JSON(evaluationResult)
	})

	fmt.Println("Sentryn Go Gateway online on port 8080...")
	log.Fatal(app.Listen(":8080"))
}